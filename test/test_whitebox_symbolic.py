import pytest
import inspect
from src.symbolic_engine import SymbolicEngine, symbolic_execute_function, generate_symbolic_tree

def test_normalize_inputs_and_ordering():
    eng = SymbolicEngine(seed=0)
    normalized = eng._normalize_inputs({"b": [2], "a": 1})

    assert list(normalized.keys()) == ["a", "b"]
    assert normalized["a"] == [1]
    assert normalized["b"] == [2]

def test_build_combinations_and_determinism():
    eng = SymbolicEngine(seed=0)
    normalized = eng._normalize_inputs({"x": [1,2], "y": [True, False]})
    combos = eng._build_combinations(normalized)

    assert len(combos) == 4
    assert combos[0] == {"x": 1, "y": True}
    
    assert combos[-1] == {"x": 2, "y": False}

def test_symbolic_execute_keyword_vs_single_positional():
    def kw_only(x, y=0):
        return x + y
    def single_pos(a):
        return a * 2
    out1 = symbolic_execute_function(kw_only, {"x": [1, 2], "y": [10]})
    assert out1["metadata"]["evaluations"] == 2
    
    out2 = symbolic_execute_function(single_pos, {"a": [3, 4]})
    assert out2["metadata"]["evaluations"] == 2

def test_exception_captured_in_path():
    def raises_on(a):
        if a < 0:
            raise ValueError("neg")
        return "ok"
    out = symbolic_execute_function(raises_on, {"a": [-1, 0]})
    excs = [p["exception"] for p in out["paths"]]
    assert any(e is not None for e in excs)
    
    assert any("ValueError" in (e or "") for e in excs)