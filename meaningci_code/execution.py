import json
import math
import subprocess
import sys
import time
from .dataset import ROOT

def run(code, function, args, timeout=1.0):
    start = time.perf_counter()
    try:
        result = subprocess.run([sys.executable, "-I", str(ROOT / "meaningci_code" / "worker.py")],
            input=json.dumps({"code": code, "function": function, "args": args}), text=True,
            capture_output=True, timeout=timeout, cwd=ROOT)
        if result.returncode != 0:
            return {"status": "harness_error", "returncode": result.returncode}
        output = json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        output = {"status": "timeout"}
    except (ValueError, OSError):
        output = {"status": "harness_error"}
    output["wall_ms"] = (time.perf_counter() - start) * 1000
    return output

def matches_expected(outcome, expected, function, args):
    if outcome["status"] != "ok":
        return False
    if function == "sqrt":
        return math.isclose(outcome["value"], expected, rel_tol=1e-6, abs_tol=args[-1])
    return outcome["value"] == expected

def differs(a, b):
    if a["status"] in ("timeout", "harness_error") or b["status"] in ("timeout", "harness_error"):
        return None
    return {k: v for k, v in a.items() if k != "wall_ms" and k != "predicates"} != {k: v for k, v in b.items() if k != "wall_ms" and k != "predicates"}

