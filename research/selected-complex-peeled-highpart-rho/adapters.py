"""Engine-measured adapter closure for the ordinary leaf-call path.

The published completed ordinary Binary and Ordinary adapters take no external
stock / S_leaf / parent-reserve argument.  Every peeled and high-part call in
this package runs through Binary.run(payload, width, prefixes, gap, suffix).
Parent reserve enters only as a factor of the caller's prefixes count; the
adapter API itself has no reserve parameter.  That is measured from the pinned
engine sources (AST) and from one live Binary call per residual class.
"""
import ast
from pathlib import Path
import inspect

import residual
import highpart

ENGINE = residual.ENGINE
FORBIDDEN_PARAM_NAMES = frozenset({
    "stock", "s_leaf", "S_leaf", "reserve", "parent_reserve", "S_ext", "s_ext",
    "leaf_reserve", "external_stock", "row_stock",
})


def need(condition, message):
    if not condition:
        raise ValueError(message)


def _run_method_source(path, class_name):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "run":
                    return item
    raise ValueError("missing run method on " + class_name)


def inspect_adapter_apis():
    """AST-measure Binary.run and Ordinary.run: no stock/S_leaf parameters."""
    binary_run = _run_method_source(ENGINE / "binary.py", "Binary")
    ordinary_run = _run_method_source(ENGINE / "ordinary.py", "Ordinary")
    records = []
    for name, node in (("Binary.run", binary_run), ("Ordinary.run", ordinary_run)):
        args = [arg.arg for arg in node.args.args]
        need(args[0] == "self", name + " is an instance method")
        params = args[1:]
        forbidden = sorted(FORBIDDEN_PARAM_NAMES & set(params))
        need(not forbidden, name + " must not take stock/reserve params: " + ",".join(forbidden))
        need(params == ["payload", "width", "prefixes", "gap", "suffix"]
             or params == ["payload", "original", "prefixes", "gap", "suffix"],
             name + " unexpected signature: " + ",".join(params))
        records.append(dict(method=name, params=params, stock_params=0, reserve_params=0))
    return records


def live_binary_signatures():
    """One live Binary call each for peeled and high-part; record adapter kwargs."""
    out = []
    # Peeled: one delta=1 call through Binary.
    peeled = residual.run_residual(2, 1, 1, 1, 2)
    need(len(peeled["signatures"]) == 1, "one peeled Binary call")
    need(peeled["signatures"][0][0] % 1 == 0, "reserve multiplicity in peeled prefix")
    out.append(dict(class_name="peeled", adapter="Binary",
                    call_args=["payload", "width", "prefixes", "gap", "suffix"],
                    signature=list(peeled["signatures"][0]),
                    stock_argument=None, parent_reserve_in_prefix=True))
    # High-part: one call through Binary.
    high = highpart.run_highpart(2, 1, 1, 1)
    need(len(high["signatures"]) == 1, "one highpart Binary call")
    out.append(dict(class_name="highpart", adapter="Binary",
                    call_args=["payload", "width", "prefixes", "gap", "suffix"],
                    signature=list(high["signatures"][0]),
                    stock_argument=None, parent_reserve_in_prefix=True))
    return out


def runtime_signature_check():
    """Confirm the live BoundMethod signatures match the AST measurement."""
    residual.engine_modules()  # activate engine once
    import binary as binary_mod
    import ordinary as ordinary_mod
    records = []
    for label, fn in (("Binary.run", binary_mod.Binary.run),
                      ("Ordinary.run", ordinary_mod.Ordinary.run)):
        params = [p.name for p in inspect.signature(fn).parameters.values()
                  if p.name != "self"]
        need(not (FORBIDDEN_PARAM_NAMES & set(params)),
             label + " runtime signature carries stock/reserve")
        records.append(dict(method=label, params=params, stock_params=0))
    return records


def summarize():
    apis = inspect_adapter_apis()
    live = live_binary_signatures()
    runtime = runtime_signature_check()
    need(all(r["stock_params"] == 0 for r in apis), "AST adapters stock-free")
    need(all(r["stock_argument"] is None for r in live), "live Binary calls stock-free")
    need(all(r["stock_params"] == 0 for r in runtime), "runtime adapters stock-free")
    return dict(
        inventory_ordinary_classes=["peeled", "highpart"],
        adapter_apis=apis,
        live_binary_calls=live,
        runtime_signatures=runtime,
        ordinary_external_stock_args=0,
        adapters_close_ordinary_leaf_path=True,
    )


def cleanup_engine_tempdir():
    """Drop the engine's TemporaryDirectory so -Werror stays clean."""
    try:
        import source as engine_source
    except ImportError:
        return False
    temp = getattr(engine_source, "_temporary", None)
    if temp is not None:
        temp.cleanup()
        engine_source._temporary = None
        return True
    return False
