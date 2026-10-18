"""Independent replay of the joint peeled+highpart certificate without the engine."""
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
        keys = [key for key, _value in items]
        need(len(keys) == len(set(keys)), "duplicate JSON key")
        return dict(items)
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs)


def product(values):
    out = 1
    for value in values:
        out *= value
    return out


def peeled_plan(nodes):
    deltas, max_calls, total = set(), 0, 0
    for n in range(nodes):
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


def peeled_fields(delta, width, reserve, middle):
    names = ["Pre", "Reserve"] + ["H%d" % i for i in range(delta)]
    sizes = [2, reserve] + [2 ** width] * delta
    if middle:
        names.append("MH")
        sizes.append(middle)
    names.append("Z")
    sizes.append(2)
    if middle:
        names.append("MD")
        sizes.append(middle)
    names += ["Dr%d" % (delta - 1 - k) for k in range(delta)]
    sizes += [2 ** width] * delta
    names.append("Post")
    sizes.append(2)
    return names, sizes


def highpart_fields(k, body, reserve):
    return (
        ["Pre", "Reserve", "H_hi", "D_body", "Z", "D_hi", "H_body", "Post"],
        [2, reserve, 2 ** k, 2 ** body, 2, 2 ** k, 2 ** body, 2],
    )


def check_adapters(certificate):
    adapters = certificate["adapters"]
    need(adapters["ordinary_external_stock_args"] == 0, "adapters stock-free")
    need(adapters["adapters_close_ordinary_leaf_path"] is True, "adapters close path")
    for api in adapters["adapter_apis"]:
        need(api["stock_params"] == 0 and api["reserve_params"] == 0, "AST stock-free")
        need("stock" not in api["params"] and "reserve" not in api["params"], "no stock name")
    for live in adapters["live_binary_calls"]:
        need(live["stock_argument"] is None, "live stock None")
        need(live["call_args"] == ["payload", "width", "prefixes", "gap", "suffix"],
             "Binary call args")


def main():
    certificate = strict(HERE / "CERTIFICATE.json")["default"]
    peeled = certificate["peeled_plan"]
    covered, max_calls, total = peeled_plan(peeled["nodes"])
    need(covered == peeled["internal_deltas_covered"] == M, "every delta in 0..72")
    need(max_calls == peeled["max_calls"] == M - 1, "at most 72 residual calls")
    need(total == peeled["total_calls"], "total residual calls")
    need(peeled["reserve_active_calls"] == 0 and peeled["S_leaf"] == 1, "peeled S_leaf=1")

    high = certificate["highpart_plan"]
    need(high["shapes"] == 25 and high["calls_per_shape"] == 1, "highpart grid")
    need(high["reserve_active_calls"] == 0 and high["S_leaf"] == 1, "highpart S_leaf=1")

    for case in certificate["peeled_physical"]:
        names, sizes = peeled_fields(case["delta"], case["width"], case["reserve"], case["middle"])
        signatures = []
        for i in range(case["delta"]):
            a, b = names.index("H%d" % i), names.index("Dr%d" % i)
            need(a > names.index("Reserve"), "reserve precedes every active field")
            signatures.append([product(sizes[:a]), product(sizes[a + 1:b]), product(sizes[b + 1:])])
        need(signatures == case["signatures"], "peeled call signatures")
        volume = product(sizes)
        need(volume == case["volume"], "peeled volume")
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
        need(sha256(bytes(final)).hexdigest() == case["final_sha256"], "peeled payload")

    for case in certificate["highpart_physical"]:
        names, sizes = highpart_fields(case["k"], case["body"], case["reserve"])
        a, b = names.index("H_hi"), names.index("D_hi")
        need(a > names.index("Reserve"), "reserve precedes highs")
        signature = [product(sizes[:a]), product(sizes[a + 1:b]), product(sizes[b + 1:])]
        need([signature] == case["signatures"], "highpart signature")
        need(product(sizes) == case["volume"], "highpart volume")
        need(case["active_width"] == case["k"], "active width k")
        need(case["full_chunk_width"] == case["k"] + case["body"], "full chunk k+body")
        data = bytes(((x * 13) ^ (x >> 3) ^ (x >> 7) ^ 0x53) & 1 for x in range(case["volume"]))
        final = bytearray(case["volume"])
        for source in range(case["volume"]):
            rest, values = source, []
            for size in reversed(sizes):
                rest, digit = divmod(rest, size)
                values.append(digit)
            values = values[::-1]
            values[a], values[b] = values[b], values[a]
            target = 0
            for value, size in zip(values, sizes):
                target = target * size + value
            final[target] = data[source]
        need(sha256(bytes(final)).hexdigest() == case["final_sha256"], "highpart payload")

    need(certificate["controls"]["peeled"] == [
        "forward_pairing", "ordinary_m64_histogram", "reserve_consuming_call",
        "omitted_residual_call"], "peeled controls")
    need(certificate["controls"]["highpart"] == [
        "body_swap_not_highpart", "unequal_high_extents", "reserve_consuming_call",
        "omitted_highpart_call"], "highpart controls")
    check_adapters(certificate)
    composition = certificate["composition"]
    need(composition["rho_peeled_highpart"] == 0, "composed rho")
    need(composition["peeled_S_leaf"] == composition["highpart_S_leaf"] == 1, "both S_leaf")
    need(composition["adapters_stock_args"] == 0, "composition adapters")
    need(composition["selected_kappa"] == "0.001672660197076918", "kappa")
    print("PASS_SELECTED_COMPLEX_PEELED_HIGHPART_RHO_INDEPENDENT "
          "peeled_nodes=%d peeled_deltas=%d/73 highpart_shapes=%d "
          "peeled_physical=%d highpart_physical=%d "
          "rho_peeled_highpart=0 adapters_stock_args=0" %
          (peeled["nodes"], covered, high["shapes"],
           len(certificate["peeled_physical"]), len(certificate["highpart_physical"])))


if __name__ == "__main__":
    main()
