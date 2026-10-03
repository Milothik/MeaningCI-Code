import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from meaningci_code.evaluation import evaluate
p = argparse.ArgumentParser()
p.add_argument('--output')
p.add_argument('--recordings')
p.add_argument('--reuse-execution')
a = p.parse_args()
print(evaluate(a.output,a.recordings,a.reuse_execution))

