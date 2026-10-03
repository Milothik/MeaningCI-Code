import ast
import concurrent.futures
import json
from datetime import datetime, timezone
from pathlib import Path
from .dataset import ROOT, dump, digest
from .execution import run, differs, matches_expected
from .providers import recording_for, score_pair, ProviderError

def rows(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]

def evaluate(output=None, recordings=None, reuse_execution=None):
    output = Path(output or ROOT / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    output.mkdir(parents=True,exist_ok=True)
    protocol = json.loads((ROOT/"benchmark/protocol.json").read_text())
    pairs = rows(ROOT/"benchmark/pairs.jsonl")
    tasks = {x["pair_id"]:x for x in rows(ROOT/"benchmark/tasks.jsonl")}
    # Gold becomes available to this evaluator, never to providers/request builders.
    gold = {x["pair_id"]:x for x in rows(ROOT/"benchmark/gold.jsonl")}
    dump(output/"config.json", {"protocol":protocol,"dataset":json.loads((ROOT/"benchmark/metadata.json").read_text()),"provider":"jev-recorded" if recordings else "unavailable",
        "recordings":str(recordings) if recordings else None,"execution_reused":bool(reuse_execution),"python":__import__('sys').version,"started_at":datetime.now(timezone.utc).isoformat()})
    dump(output/"protocol.json",protocol)
    jobs = {}
    for p in pairs:
        for code in (p["source"],p["candidate"]):
            for fixture in gold[p["pair_id"]]["fixtures"]:
                args = fixture[0] if isinstance(fixture[0],list) else [fixture[0]]
                key = digest([code,p["function"],args,protocol["execution_timeout_seconds"]])
                jobs[key] = (code,p["function"],args)
    if reuse_execution:
        cache = {x["key"]:x["outcome"] for x in rows(Path(reuse_execution)/"execution.jsonl")}
        if set(jobs)-set(cache):
            raise ValueError("Reused execution does not cover dataset")
    else:
        cache = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=protocol["execution_workers"]) as pool:
            futures = {pool.submit(run,*args,timeout=protocol["execution_timeout_seconds"]):key for key,args in jobs.items()}
            with (output/"execution.jsonl").open("w",encoding="utf-8") as file:
                for i,future in enumerate(concurrent.futures.as_completed(futures)):
                    key = futures[future]
                    cache[key] = future.result()
                    file.write(json.dumps({"key":key,"outcome":cache[key]})+"\n")
                    file.flush()
                    if (i+1)%100 == 0:
                        print("Executed %d/%d calls" % (i+1,len(jobs)),flush=True)
    if reuse_execution:
        (output/"execution.jsonl").write_text("".join(json.dumps({"key":k,"outcome":v})+"\n" for k,v in cache.items()),encoding="utf-8")
    results = []
    for p in pairs:
        g = gold[p["pair_id"]]
        outcomes = []
        for idx,fixture in enumerate(g["fixtures"]):
            args = fixture[0] if isinstance(fixture[0],list) else [fixture[0]]
            a,b = [cache[digest([code,p["function"],args,protocol["execution_timeout_seconds"]])] for code in (p["source"],p["candidate"])]
            outcomes.append({"input_index":idx,"args":args,"expected":fixture[1],"source":a,"candidate":b,
                             "source_matches_gold":matches_expected(a,fixture[1],p["function"],args),"differs":differs(a,b)})
        indexes = {o["input_index"] for o in p["observations"]}
        def test_prediction(selected):
            usable = [o for o in outcomes if o["input_index"] in selected and o["source_matches_gold"]]
            if any(o["differs"] is True for o in usable):
                return True
            if not usable or any(o["differs"] is None for o in usable):
                return None
            return False
        def ci_prediction(selected):
            # Standard CI fails a candidate on its timeout while the reference passes.
            # This is a budget violation, not proof that the function never terminates.
            usable = [o for o in outcomes if o["input_index"] in selected and o["source_matches_gold"]]
            if any(o["differs"] is True or o["candidate"]["status"] == "timeout" for o in usable):
                return True
            return test_prediction(selected)
        observations_oracle = []
        for obs in p["observations"]:
            o = outcomes[obs["input_index"]]
            a = o["source"].get("predicates",{}).get(obs["predicate"])
            b = o["candidate"].get("predicates",{}).get(obs["predicate"])
            observations_oracle.append({"id":obs["id"],"A":a,"B":b,"differs":None if a is None or b is None else a != b})
        result = {"pair_id":p["pair_id"],"program":p["program"],"split":p["split"],"gold_label":g["label"],"kind":g["kind"],
            "predictions":{"text-change":p["source"]!=p["candidate"],"ast-change":ast.dump(ast.parse(p["source"]))!=ast.dump(ast.parse(p["candidate"])),
                           "tests-budget-3":test_prediction(indexes),"tests-full":test_prediction(set(range(len(outcomes))))},
            "oracle_selected_inputs":any(o["differs"] is True for o in outcomes if o["input_index"] in indexes),
            "oracle_probe_coverage":any(x["differs"] is True for x in observations_oracle),
            "source_fixture_failures":sum(not o["source_matches_gold"] for o in outcomes),"execution":outcomes,"oracle_observations":observations_oracle}
        result["predictions"]["ci-tests-budget-3"] = ci_prediction(indexes)
        result["predictions"]["ci-tests-full"] = ci_prediction(set(range(len(outcomes))))
        if recordings:
            try:
                capture,parsed = recording_for(tasks[p["pair_id"]],recordings)
                result["jev"] = score_pair(parsed,len(p["observations"]),protocol["confidence_gate"])
                result["jev"]["usage"] = capture["response"].get("usage")
                result["jev"]["engine_time_ms"] = capture["response"].get("evaluation_time_ms")
                result["jev"]["ui_wall_ms"] = capture.get("ui_wall_ms")
                result["jev"]["model"] = capture["response"]["model"]
                result["jev"]["request_id"] = capture["response"]["request_id"]
                result["predictions"]["jev-direct"] = result["jev"]["direct_prediction"]
                result["predictions"]["meaningci-label"] = result["jev"]["label_prediction"]
            except (ProviderError,KeyError,ValueError) as exc:
                result["jev_error"] = str(exc)
        results.append(result)
    validation = [r for r in results if r["split"] == "validation" and "jev" in r]
    def classify(r,t):
        j = r["jev"]
        return True if j["jsd_score"] > t else None if j["has_uncertainty"] else False
    if validation:
        from .analysis import metrics
        threshold = max(protocol["jsd_candidates"], key=lambda t:(metrics([dict(r,predictions={"m":classify(r,t)}) for r in validation],"m")["f1"],t))
        dump(output/"frozen_thresholds.json",{"jsd_threshold":threshold,"selected_on":"validation only","validation_pairs":len(validation),"candidates":protocol["jsd_candidates"]})
        for r in results:
            if "jev" in r:
                r["predictions"]["meaningci-jsd"] = classify(r,threshold)
    (output/"results.jsonl").write_text("".join(json.dumps(r)+"\n" for r in results),encoding="utf-8")
    for r in results:
        dump(output/"traces"/(r["pair_id"]+".json"),r)
    dump(output/"logs"/"failures.json",[{"pair_id":r["pair_id"],"jev_error":r.get("jev_error"),"source_fixture_failures":r["source_fixture_failures"],"timeouts":sum(o[v]["status"]=="timeout" for o in r["execution"] for v in ("source","candidate"))} for r in results if r.get("jev_error") or r["source_fixture_failures"] or any(o[v]["status"]=="timeout" for o in r["execution"] for v in ("source","candidate"))])
    from .analysis import analyze
    analyze(output)
    return output
