"""Strict native response validation; recordings are exact replay, not inference."""
import json
import math
from pathlib import Path
from .dataset import digest

class ProviderError(RuntimeError):
    pass

def parse_response(request, response):
    if not isinstance(response.get("model"), str) or not response["model"] or not response.get("request_id"):
        raise ProviderError("Missing resolved model or request ID")
    if set(response.get("answers", {})) != set(request["questions"]):
        raise ProviderError("Incomplete or unexpected questions")
    parsed = {}
    for key, question in request["questions"].items():
        answer = response["answers"][key]
        raw = answer.get("probabilities", {})
        if set(raw) != set(question["criteria"]):
            raise ProviderError("Invalid choice set")
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0 <= v <= 1 for v in raw.values()):
            raise ProviderError("Invalid native probability")
        mass = sum(raw.values())
        if abs(mass-1) > .015000001 or mass <= 0:
            raise ProviderError("Native probability mass outside rounded tolerance")
        choice = answer.get("choice")
        confidence = answer.get("confidence")
        if choice not in raw or max(raw.values())-raw[choice] > .010000001:
            raise ProviderError("Choice and probability mismatch")
        if isinstance(confidence,bool) or not isinstance(confidence,(int,float)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ProviderError("Invalid confidence")
        p = {k:v/mass for k,v in raw.items()}
        parsed[key] = {"probabilities":p,"raw_probabilities":raw,"normalization_mass":mass,"reported_choice":choice,"confidence":confidence,"top":max(p,key=p.get)}
    return parsed

def recording_for(task, directory):
    path = Path(directory) / (task["task_id"] + ".json")
    if not path.exists():
        raise ProviderError("Missing authenticated measurement")
    capture = json.loads(path.read_text(encoding="utf-8"))
    if digest(capture["request"]) != task["task_id"] or capture["request"] != task["request"]:
        raise ProviderError("Recording content does not match request")
    if not capture.get("ui_input_verified") and capture.get("channel") != "api":
        raise ProviderError("Capture inputs were not verified")
    return capture, parse_response(task["request"], capture["response"])

def jsd(p, q):
    if set(p) != set(q):
        raise ValueError("Distributions have different choices")
    m = {k:(p[k]+q[k])/2 for k in p}
    def kl(a):
        return sum(v*math.log2(v/m[k]) for k,v in a.items() if v)
    return (kl(p)+kl(q))/2

def score_pair(parsed, count, confidence_gate=.65):
    scores, flips, uncertain = [], [], False
    for i in range(count):
        a, b = parsed["A_%02d" % i], parsed["B_%02d" % i]
        valid = all(x["top"] != "UNKNOWN" and x["probabilities"][x["top"]] >= confidence_gate for x in (a,b))
        uncertain |= not valid
        if valid:
            scores.append(jsd(a["probabilities"],b["probabilities"]))
            flips.append(a["top"] != b["top"])
    direct = parsed["direct"]
    direct_prediction = None if direct["top"] == "UNKNOWN" or direct["probabilities"][direct["top"]] < confidence_gate else direct["top"] == "CHANGED"
    return {"jsd_score":max(scores,default=0),"has_uncertainty":uncertain,"label_prediction":True if any(flips) else None if uncertain else False,
            "direct_prediction":direct_prediction,"vectors":parsed,"reliable_observations":len(scores)}

