#!/usr/bin/env python3
"""Exact evidence for seven-query shared-XOR obstruction. Wentao Li + AI, Apache-2.0.

Default verify is read-only and compares a fresh census to CERTIFICATE.json.
Admission uses need() (not assert); -O also passes. Use --write to regenerate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHECKS = 0


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise RuntimeError(message)


def load_model():
    sys.path.insert(0, str(ROOT))
    import model  # noqa: WPS433

    return model


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def git_blob(path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", f"HEAD:{path}"], text=True
    ).strip()


def check_sources(model):
    source = json.loads((ROOT / "SOURCES.json").read_text())
    need(source["schema_version"] == 1, "source schema")
    need(
        isinstance(source["base_commit"], str) and len(source["base_commit"]) == 40,
        "base pin",
    )
    for row in source["files"]:
        data = (REPO / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], f"sha256 {row['path']}")
        need(git_blob(row["path"]) == row["git_blob"], f"blob {row['path']}")
    return hashlib.sha256(canonical(source).encode()).hexdigest()


def build_certificate(model):
    words = model.restored_length_two_words()
    need(len(words) == 20, "exactly twenty restored length-2 words")
    multi_sets = {frozenset(w["mid_multi_bit_columns"]) for w in words}
    need(all(len(s) == 1 for s in multi_sets), "each mid-state exposes one multi-bit column")
    need(len(multi_sets) == 10, "ten distinct weight-2 mid columns")

    cover = model.r82_covering_sets()
    need(len(cover) == 97216, "R=82 covering set count")

    paths = model.path_x6_fullrank_increments(cover)
    need(len(paths) == 40320, "path-local X=6 full-rank path count")

    patterns = Counter()
    repeats = 0
    for incs in paths:
        info = model.multi_bit_pattern(incs)
        patterns[info["weight_pattern"]] += 1
        if info["has_repeat"]:
            repeats += 1
        need(info["distinct_multi"] >= 2, "path_X=6 schedules expose at least two distinct multis")
    need(repeats == 0, "no repeated multi-bit increments among path_X=6 paths")
    need(patterns[(2, 2, 2)] == 30240, "three weight-2 pattern count")
    need(patterns[(2, 3)] == 10080, "weight-2+3 pattern count")

    _, adj2 = model.ball_adjacency(2)
    _, adj3 = model.ball_adjacency(3)
    cheap2 = sum(1 for incs in paths if model.increments_realizable(incs, 2, adj2))
    cheap3 = sum(1 for incs in paths if model.increments_realizable(incs, 3, adj3))
    need(cheap2 == 0, "no path_X=6 schedule with interleaved X<=2")
    need(cheap3 == 0, "no path_X=6 schedule with interleaved X<=3")

    champ = model.CHAMPION_INCREMENTS
    need(champ in set(paths), "champion path among path_X=6 schedules")
    need(not model.increments_realizable(champ, 2, adj2), "champion X<=2 blocked")
    need(not model.increments_realizable(champ, 3, adj3), "champion X<=3 blocked")
    _, adj6 = model.ball_adjacency(6)
    need(model.increments_realizable(champ, 6, adj6), "champion attains interleaved X=6")

    t_end = model.ENDPOINT_Q6
    t2 = model.tariff(7, 82, 2)
    t3 = model.tariff(7, 82, 3)
    t4 = model.tariff(7, 82, 4)
    t6 = model.tariff(7, 82, 6)
    need(t2 == 434 and t2 < t_end, "X=2 would beat endpoint")
    need(t3 == 436 and t3 == t_end, "X=3 would tie endpoint")
    need(t4 == 438 and t4 > t_end, "X>=4 already above endpoint")
    need(t6 == 442, "path-local champion tariff")

    return {
        "format": "mutable-source-7q-shared-xor-certificate-v1",
        "claimed_scope": (
            "interleaved elementary source-XOR schedules realizing connector increments "
            "of full-rank path-local-X=6 walks on R=82 seven-query slot sets; "
            "PR1898 abstract tariff (38,2,2); no new kappa"
        ),
        "fixture": {
            "b": model.TARIFF_B,
            "a": model.TARIFF_A,
            "x": model.TARIFF_X,
            "endpoint_q6_tariff": t_end,
            "champion_path": list(model.CHAMPION_PATH),
            "champion_increments": list(champ),
        },
        "restored_length_two": {
            "count": len(words),
            "distinct_mid_multi_bit_column_sets": len(multi_sets),
            "max_multi_bit_columns_per_mid_state": 1,
            "words": words,
        },
        "r82_cover_sets": len(cover),
        "path_local_x6_fullrank_paths": len(paths),
        "multi_bit_patterns": {
            "weight_222": patterns[(2, 2, 2)],
            "weight_23": patterns[(2, 3)],
            "repeated_multi_bit_increments": repeats,
        },
        "interleaved_census": {
            "paths_with_X_le_2": cheap2,
            "paths_with_X_le_3": cheap3,
            "champion_X_le_2": False,
            "champion_X_le_3": False,
            "champion_X_le_6": True,
            "champion_exact_min_X": 6,
        },
        "tariffs": {
            "q7_r82_x2": t2,
            "q7_r82_x3": t3,
            "q7_r82_x4": t4,
            "q7_r82_x6": t6,
            "beats_or_ties_endpoint_requires_X_le": 3,
            "blocked_by_census": True,
        },
        "no_new_kappa": True,
    }


def reject_duplicate_keys(text: str):
    seen = []

    def hook(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            seen.append(True)
        return dict(items)

    json.loads(text, object_pairs_hook=hook)
    need(not seen, "duplicate JSON keys in certificate text")


def build_quick_checks(model):
    """Algebraic length-2 classification, champion X bounds, tariff arithmetic."""
    words = model.restored_length_two_words()
    need(len(words) == 20, "exactly twenty restored length-2 words")
    multi_sets = {frozenset(w["mid_multi_bit_columns"]) for w in words}
    need(all(len(s) == 1 for s in multi_sets), "each mid-state exposes one multi-bit column")
    need(len(multi_sets) == 10, "ten distinct weight-2 mid columns")

    champ = model.CHAMPION_INCREMENTS
    _, adj2 = model.ball_adjacency(2)
    _, adj3 = model.ball_adjacency(3)
    _, adj6 = model.ball_adjacency(6)
    need(not model.increments_realizable(champ, 2, adj2), "champion X<=2 blocked")
    need(not model.increments_realizable(champ, 3, adj3), "champion X<=3 blocked")
    need(model.increments_realizable(champ, 6, adj6), "champion attains interleaved X=6")

    t2 = model.tariff(7, 82, 2)
    t3 = model.tariff(7, 82, 3)
    t6 = model.tariff(7, 82, 6)
    need(t2 == 434 and t3 == 436 and t6 == 442, "tariff fixture")
    return {
        "restored2": len(words),
        "mid_sets": len(multi_sets),
        "champion_min_X": 6,
        "tariffs": (t2, t3, t6),
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    model = load_model()
    path = ROOT / "CERTIFICATE.json"

    if args.quick and not args.write:
        existing = path.read_text()
        reject_duplicate_keys(existing)
        cert = json.loads(existing)
        quick = build_quick_checks(model)
        need(cert["restored_length_two"]["count"] == quick["restored2"], "cert/quick restored2")
        need(
            cert["restored_length_two"]["distinct_mid_multi_bit_column_sets"]
            == quick["mid_sets"],
            "cert/quick mid_sets",
        )
        need(cert["interleaved_census"]["paths_with_X_le_2"] == 0, "cert Xle2")
        need(cert["interleaved_census"]["paths_with_X_le_3"] == 0, "cert Xle3")
        need(cert["interleaved_census"]["champion_exact_min_X"] == 6, "cert champion")
        need(cert["tariffs"]["q7_r82_x2"] == quick["tariffs"][0], "cert/quick t2")
        need(cert["tariffs"]["q7_r82_x3"] == quick["tariffs"][1], "cert/quick t3")
        need(cert["tariffs"]["q7_r82_x6"] == quick["tariffs"][2], "cert/quick t6")
        sources_digest = check_sources(model)
        print(
            "PASS_MUTABLE_SOURCE_7Q_SHARED_XOR_QUICK "
            f"restored2={quick['restored2']} mid_sets={quick['mid_sets']} "
            f"champion_min_X=6 tariffs={quick['tariffs'][0]},{quick['tariffs'][1]},{quick['tariffs'][2]} "
            f"sources={sources_digest[:12]} checks={CHECKS} no_new_kappa"
        )
        return 0

    cert = build_certificate(model)
    reject_duplicate_keys(canonical(cert))
    pretty = json.dumps(cert, indent=2, sort_keys=True) + "\n"
    if args.write:
        path.write_text(pretty)
        print("WROTE_CERTIFICATE", path)
    else:
        need(path.is_file(), "missing CERTIFICATE.json; pass --write once")
        existing = path.read_text()
        reject_duplicate_keys(existing)
        need(json.loads(existing) == cert, "certificate drift")
    sources_digest = check_sources(model)
    print(
        "PASS_MUTABLE_SOURCE_7Q_SHARED_XOR "
        f"paths6={cert['path_local_x6_fullrank_paths']} "
        f"Xle2={cert['interleaved_census']['paths_with_X_le_2']} "
        f"Xle3={cert['interleaved_census']['paths_with_X_le_3']} "
        f"champion_min_X=6 "
        f"tariffs={cert['tariffs']['q7_r82_x2']},{cert['tariffs']['q7_r82_x3']},{cert['tariffs']['q7_r82_x6']} "
        f"sources={sources_digest[:12]} "
        f"checks={CHECKS} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
