"""Optional direct-API collector. No keys committed; no silent substitute.

Console captures in benchmark/recordings can be replayed without any credentials.
Fresh collection costs credits. Set TYPESAFE_API_KEY explicitly to use this script.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from meaningci_code.dataset import ROOT, dump
from meaningci_code.evaluation import rows
from meaningci_code.providers import parse_response, ProviderError

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--split',choices=['development','validation','test','all'],default='all')
    p.add_argument('--output',default=str(ROOT/'benchmark/recordings-new'))
    a=p.parse_args()
    key=os.environ.get('TYPESAFE_API_KEY')
    if not key:raise SystemExit('Set TYPESAFE_API_KEY; no mock/fallback is used.')
    split={x['pair_id']:x['split'] for x in rows(ROOT/'benchmark/pairs.jsonl')}
    out=Path(a.output)
    for task in rows(ROOT/'benchmark/tasks.jsonl'):
        if a.split!='all' and split[task['pair_id']]!=a.split:continue
        path=out/(task['task_id']+'.json')
        if path.exists():continue
        started=time.perf_counter()
        for attempt in range(3):
            try:
                request=urllib.request.Request('https://api.typesafe.ai/v1/systemone',data=json.dumps(task['request']).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
                with urllib.request.urlopen(request,timeout=30) as response:data=json.load(response)
                parse_response(task['request'],data)
                dump(path,dict(task,response=data,channel='api',api_wall_ms=(time.perf_counter()-started)*1000,captured_at=datetime.now(timezone.utc).isoformat(),attempts=attempt+1))
                print('Collected:',task['pair_id'],flush=True)
                break
            except urllib.error.HTTPError as exc:
                if exc.code not in (429,500,502,503,504) or attempt==2:
                    dump(out/'failures'/(task['task_id']+'.json'),{'task_id':task['task_id'],'failure':'HTTP','status':exc.code,'attempts':attempt+1})
                    raise SystemExit('Jev HTTP failure recorded; collection stopped.')
            except (urllib.error.URLError,TimeoutError) as exc:
                if attempt==2:
                    dump(out/'failures'/(task['task_id']+'.json'),{'task_id':task['task_id'],'failure':'network/timeout','attempts':3})
                    raise SystemExit('Jev network failure recorded; collection stopped.')
            except ProviderError:
                dump(out/'failures'/(task['task_id']+'.json'),{'task_id':task['task_id'],'failure':'Invalid native response','attempts':attempt+1})
                raise SystemExit('Invalid Jev response recorded; no substitute used.')
            time.sleep(2**attempt)

if __name__=='__main__':main()
