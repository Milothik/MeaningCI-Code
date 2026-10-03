"""Pinned benchmark execution only. This is NOT an arbitrary-code sandbox."""
import copy
import json
import math
import sys
import types

def execute(code, function, args):
    original = copy.deepcopy(args)
    namespace = {"__name__": "benchmark_execution"}
    try:
        exec(compile(code, "<benchmark>", "exec"), namespace)
        value = namespace[function](*args)
        if isinstance(value, types.GeneratorType):
            value = list(value)
        predicates = {"raises": False, "truthy": bool(value), "equals_input": value == original[0],
            "length_matches": isinstance(value, (list, tuple, str)) and isinstance(original[0], (list, tuple, str)) and len(value) == len(original[0])}
        # JSON preserves lists; tuples explicitly normalized for JSON fixture comparison.
        json_value = json.loads(json.dumps(value, allow_nan=False))
        return {"status": "ok", "value": json_value, "mutated_args": args, "predicates": predicates}
    except Exception as exc:
        return {"status": "exception", "exception": type(exc).__name__, "mutated_args": args,
                "predicates": {"raises": True, "truthy": False, "equals_input": False, "length_matches": False}}

if __name__ == "__main__":
    item = json.load(sys.stdin)
    print(json.dumps(execute(item["code"], item["function"], item["args"]), allow_nan=False))

