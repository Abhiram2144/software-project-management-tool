import pytest
import traceback

from src.symbolic_engine import symbolic_execute_function, generate_symbolic_tree


def simple_branch(x):
    if x > 0:
        return "positive"
    elif x == 0:
        return "zero"
    else:
        return "negative"


def raises_on_negative(x):
    if x < 0:
        raise ValueError("negative not allowed")
    return f"ok:{x}"


def test_symbolic_execute_enumeration():
    inputs = {"x": [-1, 0, 2]}
    out = symbolic_execute_function(simple_branch, inputs)
    assert out["metadata"]["evaluations"] == 3
    results = {p["result"] for p in out["paths"]}
    assert results == {"negative", "zero", "positive"}


def test_generate_symbolic_tree_structure():
    inputs = {"x": [1, -2]}
    tree = generate_symbolic_tree(simple_branch, inputs)
    assert "nodes" in tree and tree["root"] == 0
    assert len(tree["nodes"]) == 2
    for node in tree["nodes"]:
        assert isinstance(node["constraints"], list)
        assert "result" in node


def test_exception_capture_in_paths():
    inputs = {"x": [-1, 0, 1]}
    out = symbolic_execute_function(raises_on_negative, inputs)
    exceptions = [p["exception"] for p in out["paths"]]
    assert any(e is not None for e in exceptions)
    captured = [e for e in exceptions if e is not None][0]
    assert "ValueError" in captured or "negative not allowed" in captured


def test_single_scalar_input():
    out = symbolic_execute_function(simple_branch, {"x": 5})
    assert out["metadata"]["evaluations"] == 1
    assert out["paths"][0]["result"] == "positive"
