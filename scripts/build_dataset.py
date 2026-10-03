import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from meaningci_code.dataset import ROOT, build
print("Prepared pairs:", build(ROOT / ".data" / "QuixBugs"))

