import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from meaningci_code.analysis import analyze
analyze(sys.argv[1])
print('Analysis saved:',sys.argv[1])

