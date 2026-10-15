"""Load source-bound predecessor modules without editing their package.

Sricharan Vagvala, substantial OpenAI Codex assistance. Apache-2.0.
"""

from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = ROOT / "research/complex-ck-two-sided"
BASELINE = HERE / "baseline.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def check_pins(root=ROOT):
    sources = json.loads((HERE / "SOURCES.json").read_text())
    checked = []
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        require(path.is_file() and not path.is_symlink(), "missing or symlinked input: " + row["path"])
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "source pin mismatch: " + row["path"])
        checked.append(row["path"])
    return checked


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def module_aliases(**modules):
    saved = {name: sys.modules.get(name) for name in modules}
    saved_path = sys.path[:]
    sys.modules.update(modules)
    try:
        yield
    finally:
        sys.path[:] = saved_path
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def predecessor():
    """Load construction/verifier against production independent.py.

    Pairwise-era bytes live in baseline.py for differential kernel checks after
    the production wiring in research/ck-dyadic-replay-production/.
    """
    check_pins()
    require(BASELINE.is_file() and not BASELINE.is_symlink(), "missing vendored baseline.py")
    require(hashlib.sha256(BASELINE.read_bytes()).hexdigest()
            == "87d690c534409047322c1dc625586adf4c192a9746941eae06c3da6e0add3aa2",
            "vendored baseline.py drift")
    experiment = load_module("ck917_experiment", PREDECESSOR / "experiment.py")
    independent = load_module("ck917_independent", PREDECESSOR / "independent.py")
    with module_aliases(experiment=experiment, independent=independent):
        verifier = load_module("ck917_verifier", PREDECESSOR / "verify.py")
    require(verifier.e is experiment and verifier.independent is independent,
            "unexpected predecessor imports")
    return experiment, independent, verifier


def pairwise_baseline():
    """Pairwise-era independent.py retained for opt-in differential evidence."""
    require(BASELINE.is_file() and not BASELINE.is_symlink(), "missing vendored baseline.py")
    return load_module("ck917_pairwise_baseline", BASELINE)


def fixture(experiment):
    word, original, _ = experiment.load()
    panel, recipe = experiment.construct(word)
    require(canonical(recipe) == canonical(experiment.read(PREDECESSOR / "RECIPE.json")),
            "recipe reconstruction changed")
    candidate = experiment.replace_programs(word, original, panel)
    return {label + "_" + orientation: list(experiment.primitives(events[orientation]))
            for label, events in (("baseline", original), ("candidate", candidate))
            for orientation in ("forward", "backward")}
