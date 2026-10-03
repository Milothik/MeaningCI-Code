import json
from pathlib import Path
from meaningci_code.dataset import ROOT, digest, request_for, renamed
from meaningci_code.evaluation import rows
from meaningci_code.providers import recording_for
from meaningci_code.analysis import analyze

def test_dataset_split_boundary_and_input_only_tasks():
    pairs=rows(ROOT/'benchmark/pairs.jsonl')
    tasks={x['pair_id']:x for x in rows(ROOT/'benchmark/tasks.jsonl')}
    grouped={}
    assert len(pairs)==93
    for pair in pairs:
        assert grouped.setdefault(pair['program'],pair['split'])==pair['split']
        assert request_for(pair,pair['observations'])==tasks[pair['pair_id']]['request']
        assert set(tasks[pair['pair_id']]['request']['state'])=={'code_A','code_B','function'}
    assert len(grouped)==31

def test_all_authentic_captures_are_exact_and_unique():
    tasks=rows(ROOT/'benchmark/tasks.jsonl')
    ids=[]
    for task in tasks:
        capture,parsed=recording_for(task,ROOT/'benchmark/recordings')
        assert capture['response']['model']=='jev-1.13.0'
        assert len(parsed)==25
        ids.append(capture['response']['request_id'])
    assert len(set(ids))==93

def test_frozen_threshold_and_all_completed_controls():
    main=ROOT/'runs/main'
    before=json.loads((ROOT/'runs/validation-freeze/frozen_thresholds.json').read_text())
    after=json.loads((main/'frozen_thresholds.json').read_text())
    assert before==after and after['validation_pairs']==24
    for r in rows(main/'results.jsonl'):
        assert 'jev' in r
        if not r['gold_label']:assert not any(o['differs'] is True for o in r['execution'])

