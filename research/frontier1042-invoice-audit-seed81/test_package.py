"""Unit tests for the seed-81 PR1042 invoice/outer audit. Apache-2.0."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402


class GroupOrder(unittest.TestCase):
    def test_formulas_agree(self):
        for n in range(1, 40):
            self.assertEqual(V.sp_order_product(n), V.sp_order_orbit(n))

    def test_brute_force_small_odd_orthogonal(self):
        self.assertEqual(V.orthogonal_odd_brute(1), 6)
        self.assertEqual(V.orthogonal_odd_brute(2), 720)


class Replay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = V.load_inputs(V.ROOT)

    def test_committed_result_regenerates(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'verify.py')], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('PASS_FRONTIER1042_INVOICE_OUTER_INDEPENDENT', r.stdout)

    def test_every_control_rejected(self):
        res = V.controls(self.data)
        self.assertEqual(len(res), 15)
        self.assertEqual(res['max_rank'], 'halving guard m^2 > 2 max^2')
        self.assertEqual(res['group_Sp70'], 'stock bits')

    def test_kappa_is_last_grid_point(self):
        out = V.run_all(self.data)
        k = Q(self.data['asm']['kappa'])
        self.assertEqual(out['native']['kappa'], str(k))
        self.assertEqual(k, Q(1672188119205421, 10 ** 18))

    def test_result_fields(self):
        res = json.loads((HERE / 'RESULT.json').read_text())
        self.assertEqual(res['guards']['row'], [16469, 20161])
        self.assertTrue(res['native']['all_quadratic'] and res['conservative']['all_quadratic'])

    def test_binds_frozen_checkpoint_not_moving_selected(self):
        selected = json.loads((V.ROOT / 'certificates/selected-result.json').read_text())
        self.assertNotEqual(selected['certificate'], V.AUDIT + '/ASSEMBLY.json')
        self.assertEqual(self.data['checkpoint_path'], V.CHECKPOINT)
        self.assertEqual(self.data['checkpoint']['certificate'], V.AUDIT + '/ASSEMBLY.json')
        self.assertEqual(self.data['checkpoint']['certificate_sha256'], V.ASSEMBLY_SHA256)


class CheckpointBindingControls(unittest.TestCase):
    """Meaningful failure controls for the checkpoint receipt pin."""

    def _stage(self):
        tmp = Path(tempfile.mkdtemp(prefix='seed81-ck-'))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        # Minimal tree: only the files load_inputs reads.
        for rel in (
            V.CHECKPOINT,
            V.AUDIT + '/ASSEMBLY.json',
            V.AUDIT + '/selected-replay.tar.gz',
            V.BIT_PATH,
        ):
            src = V.ROOT / rel
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return tmp

    def test_corrupt_checkpoint_hash_rejected(self):
        root = self._stage()
        path = root / V.CHECKPOINT
        data = json.loads(path.read_text())
        data['decimal'] = 'corrupted'
        path.write_text(json.dumps(data, indent=2) + '\n')
        with self.assertRaises(V.Fail) as ctx:
            V.load_inputs(root)
        self.assertIn('checkpoint receipt hash mismatch', str(ctx.exception))

    def test_corrupt_certificate_sha_field_rejected(self):
        root = self._stage()
        path = root / V.CHECKPOINT
        data = json.loads(path.read_text())
        data['certificate_sha256'] = '0' * 64
        # Keep the outer file hash check from firing first by rewriting the pin
        # constant through a temporary monkeypatch after writing matching bytes.
        raw = json.dumps(data, indent=2, sort_keys=True) + '\n'
        path.write_text(raw)
        # Bypass byte-hash pin to reach the field pin.
        old = V.CHECKPOINT_SHA256
        V.CHECKPOINT_SHA256 = hashlib.sha256(raw.encode()).hexdigest()
        self.addCleanup(setattr, V, 'CHECKPOINT_SHA256', old)
        with self.assertRaises(V.Fail) as ctx:
            V.load_inputs(root)
        self.assertIn('checkpoint certificate_sha256 pin mismatch', str(ctx.exception))

    def test_assembly_byte_corruption_rejected(self):
        root = self._stage()
        asm_path = root / V.AUDIT / 'ASSEMBLY.json'
        asm = json.loads(asm_path.read_text())
        # Exact rational endpoint bump that preserves kappa text if edited carefully;
        # here we corrupt a profile count so the assembly hash diverges.
        asm['complex_profile']['1'] = int(asm['complex_profile']['1']) + 1
        asm_path.write_text(json.dumps(asm, indent=2, sort_keys=True) + '\n')
        with self.assertRaises(V.Fail) as ctx:
            V.load_inputs(root)
        self.assertIn('ASSEMBLY.json does not match the checkpoint pin', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
