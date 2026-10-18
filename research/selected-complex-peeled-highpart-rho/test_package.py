"""Package tests: duplicate keys, temp corruption, -O admission, pins, controls, read-only replay."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify  # noqa: E402
from residual import need  # noqa: E402
import adapters  # noqa: E402


def package_hashes():
    return {path.name: sha256(path.read_bytes()).hexdigest()
            for path in sorted(HERE.iterdir()) if path.is_file()}


def run(*args):
    return subprocess.run([sys.executable, "-I", "-B", *args], capture_output=True, text=True)


def run_optimized(*args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", *args], capture_output=True, text=True)


def main():
    before = package_hashes()
    groups = 0

    for path in HERE.glob("*.json"):
        verify.strict_json(path)
    try:
        bad = Path(tempfile.mkdtemp()) / "dup.json"
        bad.write_text('{"a": 1, "a": 2}', encoding="utf-8")
        verify.strict_json(bad)
        raise RuntimeError("duplicate key admitted")
    except ValueError:
        groups += 1

    with tempfile.TemporaryDirectory() as tmp:
        corrupt = Path(tmp) / "CERTIFICATE.json"
        shutil.copy(HERE / "CERTIFICATE.json", corrupt)
        data = json.loads(corrupt.read_text(encoding="utf-8"))
        data["default"]["composition"]["rho_peeled_highpart"] = 1
        corrupt.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        for runner in (run, run_optimized):
            result = runner(str(HERE / "verify.py"), "--certificate", str(corrupt))
            need(result.returncode != 0 and "CERTIFICATE.json" in result.stderr,
                 "corrupted certificate rejected (incl. -O)")
        data = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
        data["default"]["peeled_physical"][0]["final_sha256"] = "0" * 64
        corrupt.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = run_optimized(str(HERE / "verify.py"), "--certificate", str(corrupt))
        need(result.returncode != 0, "corrupted peeled payload hash rejected under -O")
        groups += 1

    manifest = verify.strict_json(HERE / "SOURCES.json")
    for index, entry in enumerate(manifest["files"]):
        if entry.get("role") == "engine" and entry["path"].endswith("binary.py"):
            break
    altered = json.loads(json.dumps(manifest))
    altered["files"][index]["sha256"] = "f" * 64
    try:
        verify.check_sources(altered)
        raise RuntimeError("altered engine pin admitted")
    except ValueError as error:
        need("binary.py" in str(error), "engine pin failure names the file")
    trimmed = json.loads(json.dumps(manifest))
    trimmed["files"] = [entry for entry in trimmed["files"]
                        if not entry["path"].endswith("ordinary.py")]
    try:
        verify.check_sources(trimmed)
        raise RuntimeError("unpinned engine module admitted")
    except ValueError as error:
        need("pinned" in str(error), "unpinned engine module rejected")
    groups += 1

    original = verify.CITATIONS
    try:
        verify.CITATIONS = {"notes/stopped-product-interface.tex": ("pair the first delta tail atoms",)}
        verify.check_citations()
        raise RuntimeError("missing citation admitted")
    except ValueError:
        groups += 1
    finally:
        verify.CITATIONS = original

    verify.check_sources()
    need(verify.peeled_controls() == ["forward_pairing", "ordinary_m64_histogram",
                                      "reserve_consuming_call", "omitted_residual_call"],
         "peeled controls rejected")
    need(verify.highpart_controls() == ["body_swap_not_highpart", "unequal_high_extents",
                                        "reserve_consuming_call", "omitted_highpart_call"],
         "highpart controls rejected")
    apis = adapters.inspect_adapter_apis()
    need(all(r["stock_params"] == 0 for r in apis), "adapter AST stock-free")
    groups += 1

    for runner in (run, run_optimized):
        result = runner(str(HERE / "verify.py"))
        need(result.returncode == 0 and "PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO " in result.stdout,
             "default verify passes: " + result.stderr)
    result = run(str(HERE / "independent.py"))
    need(result.returncode == 0 and "PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO_INDEPENDENT" in result.stdout,
         "independent replay passes")
    need(package_hashes() == before, "package files unchanged by replay")
    groups += 1
    adapters.cleanup_engine_tempdir()
    print("PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO_TESTS groups=%d" % groups)


if __name__ == "__main__":
    main()
