#!/usr/bin/env python3
"""Producer for CERTIFICATE.json. Not part of the replay."""

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("flag1_late_verify", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def main():
    cert = json.loads(json.dumps(V.receipt(V.ROOT)))
    (HERE / "CERTIFICATE.json").write_text(json.dumps(cert, indent=1, sort_keys=True) + "\n")
    V.admit(V.ROOT, cert)
    print("wrote CERTIFICATE.json")


if __name__ == "__main__":
    main()
