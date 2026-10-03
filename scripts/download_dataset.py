import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from meaningci_code.dataset import ROOT, UPSTREAM, REVISION
target = ROOT / ".data" / "QuixBugs"
if not target.exists():
    subprocess.run(["git", "clone", UPSTREAM, str(target)], check=True)
actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
if actual != REVISION:
    subprocess.run(["git", "fetch", "origin", REVISION], cwd=target, check=True)
    subprocess.run(["git", "checkout", "--detach", REVISION], cwd=target, check=True)
print("Pinned QuixBugs:", REVISION)

