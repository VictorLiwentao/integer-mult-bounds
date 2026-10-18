"""Independent replay of the committed peeled-residual certificate.

Does not import residual.py, verify.py or the ordinary engine.  It rebuilds the
m=73 peel plan by list simulation, recomputes every physical call signature by
slicing the field list, and recomputes each final payload by a direct
mixed-radix digit exchange; the physical payload hashes in CERTIFICATE.json came
from the engine, so agreement checks the engine outputs from outside.
"""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
M = 73


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict(path):
    def pairs(items):
        keys = [key for key, _ in items]
        need(len(keys) == len(set(keys)), "duplicate JSON key")
        return dict(items)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def plan(limit):
    deltas, max_calls, total = set(), 0, 0
    for n in range(limit):
        head = [("H", k) for k in range(n)]
        tail = [("D", k) for k in range(n)]
        want_head, want_tail = tail[::-1], head[::-1]
        delta = n % M if n >= M else n
        h, d = list(head), list(tail)
        for i in range(delta):
            h[i], d[n - 1 - i] = d[n - 1 - i], h[i]
        block = n - delta
        old_h, old_d = h[delta:], d[:block]
        h[delta:], d[:block] = old_d[::-1], old_h[::-1]
        need(h == want_head and d == want_tail, "list simulation of F_n")
        if n >= M:
            deltas.add(delta)
        max_calls = max(max_calls, delta)
        total += delta
    return len(deltas), max_calls, total


def fields_for(delta, width, reserve, middle):
    names = ["Pre", "Reserve"] + ["H%d" % i for i in range(delta)]
    sizes = [2, reserve] + [2 ** width] * delta
    if middle:
        names.append("MH"), sizes.append(middle)
    names.append("Z"), sizes.append(2)
    if middle:
        names.append("MD"), sizes.append(middle)
    names += ["Dr%d" % (delta - 1 - k) for k in range(delta)]
    sizes += [2 ** width] * delta
    names.append("Post"), sizes.append(2)
    return names, sizes


def product(values):
    out = 1
    for value in values:
        out *= value
    return out


def main():
    certificate = strict(HERE / "CERTIFICATE.json")["default"]
    covered, max_calls, total = plan(certificate["plan"]["nodes"])
    need(covered == certificate["plan"]["internal_deltas_covered"] == M, "every delta in 0..72")
    need(max_calls == certificate["plan"]["max_calls"] == M - 1, "at most 72 residual calls")
    need(total == certificate["plan"]["total_calls"], "total residual calls")
    need(certificate["plan"]["reserve_active_calls"] == 0, "reserve never active")
    for case in certificate["physical"]:
        names, sizes = fields_for(case["delta"], case["width"], case["reserve"], case["middle"])
        signatures = []
        for i in range(case["delta"]):
            a, b = names.index("H%d" % i), names.index("Dr%d" % i)
            need(a > names.index("Reserve"), "reserve precedes every active field")
            signatures.append([product(sizes[:a]), product(sizes[a + 1:b]), product(sizes[b + 1:])])
        need(signatures == case["signatures"], "call signatures")
        volume = product(sizes)
        need(volume == case["volume"], "volume")
        data = bytes(((x * 13) ^ (x >> 3) ^ (x >> 7) ^ 0x53) & 1 for x in range(volume))
        final = bytearray(volume)
        for source in range(volume):
            rest, values = source, []
            for size in reversed(sizes):
                rest, digit = divmod(rest, size)
                values.append(digit)
            values = dict(zip(names, values[::-1]))
            for i in range(case["delta"]):
                values["H%d" % i], values["Dr%d" % i] = values["Dr%d" % i], values["H%d" % i]
            target = 0
            for name, size in zip(names, sizes):
                target = target * size + values[name]
            final[target] = data[source]
        need(sha256(bytes(final)).hexdigest() == case["final_sha256"], "engine payload endpoint")
    need(certificate["controls"] == ["forward_pairing", "ordinary_m64_histogram",
                                     "reserve_consuming_call", "omitted_residual_call"], "controls")
    print("PASS_SELECTED_COMPLEX_PEELED_LEAF_INDEPENDENT nodes=%d deltas=%d/73 max_calls=%d "
          "physical_cases=%d engine_payloads_match" %
          (certificate["plan"]["nodes"], covered, max_calls, len(certificate["physical"])))


if __name__ == "__main__":
    main()
