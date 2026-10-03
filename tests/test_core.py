import ast
from meaningci_code.dataset import clean, renamed, observations, request_for
from meaningci_code.worker import execute
from meaningci_code.execution import run, differs, matches_expected

def test_strip_alternate_implementation():
    assert 'broken' not in clean('def f():\n return 1\n"""def broken(): return 9"""')

def test_rename_preserves_signature_and_behavior():
    code = 'def f(xs):\n y = 2\n return [x*y for x in xs]\n'
    candidate, mapping = renamed(code)
    assert mapping and 'xs' in candidate
    assert execute(code, 'f', [[1,2]])['value'] == execute(candidate, 'f', [[1,2]])['value']

def test_input_only_probes_and_payload():
    obs = observations([[1],[2],[3],[4]], 'f')
    assert len(obs) == 12 and obs == observations([[1],[2],[3],[4]], 'f')
    payload = request_for({'function':'f','source':'def f(x): return x','candidate':'def f(x): return x+1'}, obs)
    assert len(payload['questions']) == 25
    assert not any(k in payload for k in ('gold', 'expected', 'label'))

def test_execution_mutation_generator_exception():
    assert execute('def f(x):\n x.append(3)\n yield from x', 'f', [[1]])['value'] == [1,3]
    out = execute('def f(x): return 1/0', 'f', [1])
    assert out['status'] == 'exception' and out['predicates']['raises']

def test_timeout_is_not_pass():
    assert run('def f(x):\n while True: pass', 'f', [1], timeout=.15)['status'] == 'timeout'
    assert differs({'status':'timeout'},{'status':'ok','value':1}) is None

def test_numeric_tolerance():
    assert matches_expected({'status':'ok','value':1.0001},1,'sqrt',[1,.001])

