from typing import Callable, Dict, Any, List
import itertools
import traceback
import random
import inspect

__all__ = ["SymbolicEngine", "symbolic_execute_function", "generate_symbolic_tree"]

class SymbolicEngine:
    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        random.seed(seed)

    def _normalize_inputs(self, inputs: Dict[str, Any]) -> Dict[str, List[Any]]:
        normalized: Dict[str, List[Any]] = {}
        for k in sorted(inputs.keys()):
            v = inputs[k]
            if isinstance(v, (list, tuple, set)):
                normalized[k] = list(v)
            else:
                normalized[k] = [v]
        return normalized

    def _build_combinations(self, normalized: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        keys = list(normalized.keys())
        pools = [normalized[k] for k in keys]
        combos = []
        for prod in itertools.product(*pools):
            combo = dict(zip(keys, prod))
            combos.append(combo)
        return combos

    def symbolic_execute_function(self, func: Callable, inputs: Dict[str, Any]) -> Dict[str, Any]:
        normalized = self._normalize_inputs(inputs)
        combos = self._build_combinations(normalized)
        paths: List[Dict[str, Any]] = []

        func_name = getattr(func, "__name__", repr(func))
        for combo in combos:
            constraints = [f"{k}=={repr(v)}" for k, v in combo.items()]
            try:
                try:
                    result = func(**combo)
                except TypeError:
                    sig = None
                    try:
                        sig = inspect.signature(func)
                    except (ValueError, TypeError):
                        sig = None
                    if sig is not None and len(sig.parameters) == 1:
                        result = func(next(iter(combo.values())))
                    else:
                        raise
                exc = None
            except Exception:
                result = None
                exc = traceback.format_exc()

            if result is None or isinstance(result, (bool, int, float, str)):
                stored_result = result
            else:
                try:
                    if isinstance(result, (list, dict, tuple)):
                        stored_result = result
                    else:
                        stored_result = repr(result)
                except Exception:
                    stored_result = repr(result)

            paths.append({"constraints": constraints, "result": stored_result, "exception": exc})

        metadata = {"evaluations": len(paths), "function": func_name, "args": list(normalized.keys())}
        return {"paths": paths, "metadata": metadata}

    def generate_symbolic_tree(self, func: Callable, inputs: Dict[str, Any]) -> Dict[str, Any]:
        out = self.symbolic_execute_function(func, inputs)
        nodes = []
        for idx, p in enumerate(out["paths"]):
            nodes.append({"id": idx, "constraints": p["constraints"], "result": p["result"], "exception": p["exception"]})
        return {"nodes": nodes, "root": 0 if nodes else None, "metadata": out["metadata"]}

_default_engine = SymbolicEngine(seed=0)

def symbolic_execute_function(func: Callable, inputs: Dict[str, Any]) -> Dict[str, Any]:
    return _default_engine.symbolic_execute_function(func, inputs)

def generate_symbolic_tree(func: Callable, inputs: Dict[str, Any]) -> Dict[str, Any]:
    return _default_engine.generate_symbolic_tree(func, inputs)

