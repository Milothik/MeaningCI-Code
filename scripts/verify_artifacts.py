"""Verify dataset, no-gold task boundary, captures and measured controls."""
import ast
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from meaningci_code.dataset import ROOT, digest, request_for, renamed
from meaningci_code.evaluation import rows
from meaningci_code.providers import recording_for

def verify(run=None):
    pairs=rows(ROOT/'benchmark/pairs.jsonl')
    gold={x['pair_id']:x for x in rows(ROOT/'benchmark/gold.jsonl')}
    tasks={x['pair_id']:x for x in rows(ROOT/'benchmark/tasks.jsonl')}
    metadata=json.loads((ROOT/'benchmark/metadata.json').read_text())
    assert len(pairs)==93 and len({p['program'] for p in pairs})==31
    assert len(metadata['excluded'])==9 and digest(pairs)==metadata['dataset_sha256']
    splits={}
    captures=0
    for p in pairs:
        assert splits.setdefault(p['program'],p['split'])==p['split']
        task=tasks[p['pair_id']]
        assert task['request']==request_for(p,p['observations'])
        assert digest(task['request'])==task['task_id']
        assert set(task['request']['state'])=={'function','code_A','code_B'}
        assert len(task['request']['questions'])==25
        g=gold[p['pair_id']]
        if g['kind']=='presentation':assert ast.dump(ast.parse(p['source']))==ast.dump(ast.parse(p['candidate']))
        if g['kind']=='rename':assert renamed(p['source'])[0]==p['candidate']
        if (ROOT/'benchmark/recordings'/(task['task_id']+'.json')).exists():
            recording_for(task,ROOT/'benchmark/recordings');captures+=1
    if run:
        results=rows(Path(run)/'results.jsonl')
        assert len(results)==93 and {r['pair_id'] for r in results}==set(gold)
        # All controls must preserve observed behavior where both executions completed.
        changed_controls=[r['pair_id'] for r in results if not r['gold_label'] and any(o['differs'] is True for o in r['execution'])]
        assert not changed_controls,changed_controls
        if captures==93:assert all('jev' in r and not r.get('jev_error') for r in results)
        thresholds=json.loads((Path(run)/'frozen_thresholds.json').read_text()) if captures==93 else None
        if thresholds:assert thresholds['validation_pairs']==24
    print(json.dumps({'dataset_valid':True,'pairs':93,'programs':31,'captures_verified':captures,'controls_validated':bool(run)}))

if __name__=='__main__':verify(sys.argv[1] if len(sys.argv)>1 else None)

