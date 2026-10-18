#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral and source-boundary controls (admitted under -O)."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import (  # noqa: E402
    ROOT,
    build,
    diagonal_fixture,
    expand_and_net_to_diagonal,
    geometry,
    j_extension_fixture,
    named_class_cost,
    need,
    pairing_rank,
    sources,
)


class Controls(unittest.TestCase):
    def test_complete_plane_not_scalar_line(self):
        planes, _matching = geometry()
        self.assertEqual(pairing_rank(planes[0], planes[0]), 2)
        self.assertEqual(pairing_rank(planes[0][:1], planes[0][:1]), 1)

    def test_named_class_opt_and_universal_floor(self):
        result = json.loads((HERE / "RESULT.json").read_bytes())
        self.assertEqual(result["named_class_optimum"], 224)
        self.assertEqual(result["j_free_floor_cited"], "45")
        self.assertTrue(result["universal_j_free_floor_applies"])
        self.assertEqual(result["pair_expansion_lemma"]["min_slack"], 4)
        self.assertTrue(result["subgradient_certificate"]["diagonal_is_critical_point"])

    def test_reductions_preserve_cost(self):
        planes, matching = geometry()
        for factory in (diagonal_fixture, j_extension_fixture):
            fixture = factory(planes, matching)
            reduced = expand_and_net_to_diagonal(planes, matching, fixture)
            self.assertEqual(reduced["post_cost"], 224)
            self.assertLessEqual(reduced["post_cost"], fixture["cost"])
            self.assertEqual(reduced["net_j_after"], 0)

    def test_lattice_above_diagonal(self):
        planes, matching = geometry()
        self.assertEqual(named_class_cost(0, {}, planes, matching), 224)
        self.assertEqual(named_class_cost(1, {}, planes, matching), 16097)
        self.assertGreater(named_class_cost(-1, {}, planes, matching), 224)

    def test_build_matches_receipt(self):
        self.assertEqual(build(), json.loads((HERE / "RESULT.json").read_bytes()))

    def manifest_control(self, change):
        doc = json.loads((HERE / "SOURCES.json").read_bytes())
        change(doc)
        with tempfile.TemporaryDirectory(prefix="c5-jfree-control-") as temp:
            path = Path(temp) / "SOURCES.json"
            path.write_text(json.dumps(doc))
            with self.assertRaises(ValueError):
                sources(ROOT, path)

    def test_manifest_inventory_and_usage(self):
        self.manifest_control(lambda d: d["files"].pop())
        self.manifest_control(
            lambda d: d["files"].append(copy.deepcopy(d["files"][-1]))
        )
        self.manifest_control(lambda d: d["files"][-1].update(usage="provenance"))
        self.manifest_control(lambda d: d["files"][-1].update(path="unexpected.json"))
        self.manifest_control(lambda d: d["files"][-1].update(extra=True))

    def test_authentication_and_actual_corruption(self):
        self.manifest_control(lambda d: d["files"][-1].update(sha256="0" * 64))
        self.manifest_control(lambda d: d["files"][-1].update(git_blob="0" * 40))
        with tempfile.TemporaryDirectory(prefix="c5-jfree-input-") as temp:
            root = Path(temp)
            for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
                if row["usage"] == "input":
                    target = root / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((ROOT / row["path"]).read_bytes())
            planes, matching = geometry(root)
            self.assertEqual(len(planes), 56)
            diagonal_fixture(planes, matching)
            target.write_bytes(target.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                geometry(root)

    def test_duplicate_json_key_rejected_in_receipt_copy(self):
        raw = (HERE / "RESULT.json").read_text()
        mutated = json.loads(raw)
        mutated["universal_j_free_floor_applies"] = False
        with tempfile.TemporaryDirectory(prefix="c5-jfree-receipt-") as temp:
            path = Path(temp) / "RESULT.json"
            path.write_text(json.dumps(mutated, indent=2, sort_keys=True) + "\n")
            with self.assertRaises(ValueError):
                need(
                    build() == json.loads(path.read_bytes()),
                    "corrupted receipt must not match",
                )

    def test_controls_survive_optimization(self):
        with self.assertRaises(ValueError):
            need(False, "must fail with -O too")


if __name__ == "__main__":
    unittest.main()
