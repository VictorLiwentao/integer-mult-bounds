#!/usr/bin/env python3
"""Run PR621's exact checks with zero-coefficient row updates omitted.

Ali Romman's original verifier remains byte-pinned and unchanged. Adapter by
thakrarsagar with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SOURCE = PACKAGE.parent / 'prime-power-cyclic-inverse'
# Pairwise-era bytes after research/cyclic-zero-production/; production verify.py
# now ships the zero-row skip. Keep the historical adapter pinned to baseline.py.
BASELINE = PACKAGE / 'baseline.py'
PINS = json.loads((PACKAGE / 'SOURCE.json').read_text())['files']
ANCHOR = '            value = a[row][col]\n            for j'
GUARD = '            value = a[row][col]\n            if value == k.zero:\n                continue\n            for j'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prepare(data, fast):
    require(hashlib.sha256(data).hexdigest() == PINS['verify.py'],
            'Predecessor verifier source changed')
    text = data.decode('utf-8')
    require(text.count(ANCHOR) == 1, 'Expected exactly one elimination anchor')
    return text.replace(ANCHOR, GUARD) if fast else text


def load(fast):
    namespace = {'__name__': 'cyclic_verifier', '__file__': str(BASELINE)}
    exec(compile(prepare(BASELINE.read_bytes(), fast),
                 str(BASELINE), 'exec'), namespace)
    return namespace


if __name__ == '__main__':
    code = prepare(BASELINE.read_bytes(), True)
    exec(compile(code, str(BASELINE), 'exec'),
         {'__name__': '__main__', '__file__': str(BASELINE)})
