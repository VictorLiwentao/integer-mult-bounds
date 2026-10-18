"""Independent replay of the committed high-part-exchange certificate.

Does not import highpart.py, verify.py or the ordinary engine.  It rebuilds
each (k, body) plan by field-list arithmetic, recomputes every physical call
signature by slicing the field list, and recomputes each final payload by a
direct mixed-radix digit exchange; the physical payload hashes in
CERTIFICATE.json came from the engine, so agreement checks the engine outputs
from outside.
"""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict(path):
    def pairs(items):
        keys = [key for key, _ in items]
        need(len(keys) == len(set(keys)), "duplicate JSON key")
        return dict(items)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def fields_for(k, body, reserve):
    names = ["Pre", "Reserve", "H_hi", "D_body", "Z", "D_hi", "H_body", "Post"]
    sizes = [2, reserve, 2 ** k, 2 ** body, 2, 2 ** k, 2 ** body, 2]
    return names, sizes


def product(values):
    out = 1
    for value in values:
        out *= value
    return out


def plan_grid():
    ratios = []
    for k in range(1, 6):
        for body in range(1, 6):
            names, sizes = fields_for(k, body, 1)
            need(names == ["Pre", "Reserve", "H_hi", "D_body", "Z", "D_hi", "H_body", "Post"],
                 "layout")
            a, b = names.index("H_hi"), names.index("D_hi")
            need(a > names.index("Reserve"), "reserve precedes highs")
            sig = [product(sizes[:a]), product(sizes[a + 1:b]), product(sizes[b + 1:])]
            need(sig[0] * (2 ** k) * sig[1] * (2 ** k) * sig[2] == product(sizes), "cover")
            ratios.append("%d/%d" % (k + body, k))
    return ratios


def main():
    certificate = strict(HERE / "CERTIFICATE.json")["default"]
    ratios = plan_grid()
    need(len(ratios) == certificate["plan"]["shapes"] == 25, "5x5 plan grid")
    need(certificate["plan"]["calls_per_shape"] == 1, "one call")
    need(certificate["plan"]["reserve_active_calls"] == 0, "reserve never active")
    need(certificate["plan"]["min_width_ratio"] == "2/1", "min width ratio")
    need(certificate["plan"]["max_width_ratio"] == "6/1", "max width ratio")
    for case in certificate["physical"]:
        names, sizes = fields_for(case["k"], case["body"], case["reserve"])
        a, b = names.index("H_hi"), names.index("D_hi")
        signatures = [[product(sizes[:a]), product(sizes[a + 1:b]), product(sizes[b + 1:])]]
        need(signatures == case["signatures"], "call signatures")
        volume = product(sizes)
        need(volume == case["volume"], "volume")
        need(case["calls"] == 1 and case["active_width"] == case["k"], "exact after cost")
        need(case["full_chunk_width"] == case["k"] + case["body"], "exact before cost")
        data = bytes(((x * 13) ^ (x >> 3) ^ (x >> 7) ^ 0x53) & 1 for x in range(volume))
        final = bytearray(volume)
        for source in range(volume):
            rest, values = source, []
            for size in reversed(sizes):
                rest, digit = divmod(rest, size)
                values.append(digit)
            values = dict(zip(names, values[::-1]))
            values["H_hi"], values["D_hi"] = values["D_hi"], values["H_hi"]
            target = 0
            for name, size in zip(names, sizes):
                target = target * size + values[name]
            final[target] = data[source]
        need(sha256(bytes(final)).hexdigest() == case["final_sha256"], "engine payload endpoint")
    need(certificate["controls"] == ["body_swap_not_highpart", "unequal_high_extents",
                                     "reserve_consuming_call", "omitted_highpart_call"],
         "controls")
    print("PASS_SELECTED_COMPLEX_HIGHPART_LEAF_INDEPENDENT shapes=%d calls=1 "
          "physical_cases=%d engine_payloads_match" %
          (certificate["plan"]["shapes"], len(certificate["physical"])))


if __name__ == "__main__":
    main()
