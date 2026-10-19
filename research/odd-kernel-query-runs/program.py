"""Odd-kernel native BIT query-run batching; VALUE addition is XOR.

Extends the dyadic-run walk of research/dyadic-query-runs to odd kernels q:
for a finite index set J, the completed batch

    D_{q,J}(x,y,z) = (x + sum_{j in J}(h^(q·2^j)+h^(-q·2^j)) y, y, z)

uses the signed q-dyadic alphabet {±q·2^k : k>=0}. Admission follows
research/odd-kernel-query-pair: odd moduli coprime to q. Typed child counts
match the dyadic formula 2r+c and do not improve for larger q.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd


def need(condition, message):
    if not condition:
        raise ValueError(message)


def odd_kernel_power(j, sign=1, kernel=1):
    need(type(j) is int and j >= 0, "nonnegative dyadic index")
    need(type(sign) is int and sign in (-1, 1), "integer sign")
    need(type(kernel) is int and kernel > 0 and kernel % 2 == 1, "positive odd kernel")
    return sign * kernel * (1 << j)


def odd_part(n):
    n = abs(int(n))
    while n % 2 == 0 and n:
        n //= 2
    return n


def is_q_dyadic(k, kernel):
    """Nonzero integer whose odd part equals the odd kernel."""
    need(type(kernel) is int and kernel > 0 and kernel % 2 == 1, "odd kernel")
    return type(k) is int and k != 0 and odd_part(k) == kernel


def address_word(k):
    """Seven events for M(k)=I+(k/4) s r^T; k nonzero integer."""
    need(type(k) is int and k != 0, "nonzero integer query power")
    a = Fraction(k, 4)
    return (
        ("affine", 2, Fraction(1), ((0, Fraction(-1)),)),
        ("affine", 3, Fraction(1), ((0, Fraction(1)),)),
        ("affine", 5, a, ((0, 1 + a), (2, -a), (3, -a))),
        ("child", 0, 5),
        ("affine", 2, Fraction(1), ((0, Fraction(1)),)),
        ("affine", 3, Fraction(1), ((0, Fraction(-1)),)),
        ("affine", 5, -1 / a, ((0, 1 / a - 1), (2, Fraction(1)),
                              (3, Fraction(1)))),
    )


def word_denominators(word):
    dens = set()
    for event in word:
        if event[0] != "affine":
            continue
        dens.add(Fraction(event[2]).denominator)
        for _, c in event[3]:
            dens.add(Fraction(c).denominator)
    return dens


def modulus_admits(k, modulus):
    need(type(modulus) is int and modulus >= 2, "modulus at least two")
    if modulus % 2 == 0:
        return False
    dens = word_denominators(address_word(k))
    for d in dens:
        if gcd(d, modulus) != 1:
            return False
    return True


def modulus_admits_kernel(kernel, modulus):
    need(type(kernel) is int and kernel > 0 and kernel % 2 == 1, "odd kernel")
    need(type(modulus) is int and modulus >= 2, "modulus")
    return modulus % 2 == 1 and gcd(modulus, kernel) == 1


def push_matrix(k):
    s = (1, 0, 1, -1, 0, -1)
    r = (1, 0, -1, -1, 0, 1)
    c = Fraction(k, 4)
    return tuple(
        tuple((Fraction(1) if i == j else Fraction(0)) + c * s[i] * r[j] for j in range(6))
        for i in range(6)
    )


def run_address(address, word, modulus=None):
    need(len(address) >= 6, "six ADDRESS fields")
    if modulus is None:
        reduce = Fraction
        state = list(map(Fraction, address))
    else:
        need(type(modulus) is int and modulus >= 3 and modulus % 2 == 1,
             "odd residue modulus at least three")
        for dens in word_denominators(word):
            need(gcd(dens, modulus) == 1, "denominator not invertible on this modulus")
        need(all(type(x) is int for x in address), "integer residue coordinates")

        def reduce(value):
            value = Fraction(value)
            return value.numerator * pow(value.denominator, -1, modulus) % modulus

        state = [x % modulus for x in address]
    for event in word:
        if event[0] == "child":
            _, first, last = event
            state[first], state[last] = state[last], state[first]
        else:
            _, target, diagonal, controls = event
            state[target] = reduce(diagonal) * state[target] + sum(
                reduce(c) * state[i] for i, c in controls
            )
            if modulus is not None:
                state[target] %= modulus
    return tuple(state)


def consecutive_runs(indices):
    """Maximal consecutive runs of a nonempty finite index set."""
    need(indices, "nonempty index set")
    ordered = sorted(set(indices))
    need(all(type(j) is int and j >= 0 for j in ordered), "nonnegative indices")
    runs = []
    start = prev = ordered[0]
    for j in ordered[1:]:
        if j == prev + 1:
            prev = j
            continue
        runs.append((start, prev))
        start = prev = j
    runs.append((start, prev))
    return tuple(runs)


def run_vertices(low, high, kernel):
    """Cumulative powers for one consecutive run [low, high]."""
    need(type(low) is int and type(high) is int and 0 <= low <= high, "run bounds")
    need(type(kernel) is int and kernel > 0 and kernel % 2 == 1, "odd kernel")
    neg = [-kernel * (1 << j) for j in range(high, low - 1, -1)]
    pos = [kernel * (1 << j) for j in range(low, high + 1)]
    return (0,) + tuple(neg) + tuple(pos) + (0,)


def run_program(low, high, kernel):
    """Walk for one consecutive run: Q on each edge; XOR at every nonzero vertex."""
    verts = run_vertices(low, high, kernel)
    events = []
    for i in range(len(verts) - 1):
        delta = verts[i + 1] - verts[i]
        need(is_q_dyadic(delta, kernel), f"edge not q-dyadic: {delta}")
        events.append(("query", 0, delta))
        if verts[i + 1] != 0:
            events.append(("xor", 0, 1))
    return tuple(events)


def batch_program(indices, kernel=1):
    """Concatenate run walks for every maximal consecutive run of J."""
    parts = []
    for low, high in consecutive_runs(indices):
        parts.extend(run_program(low, high, kernel))
    return tuple(parts)


def separate_pairs_program(indices, kernel=1):
    """Baseline: concatenate one #2687/#840 fused pair per index."""
    events = []
    for j in sorted(set(indices)):
        a = odd_kernel_power(j, 1, kernel)
        events.extend(
            (
                ("query", 0, -a),
                ("xor", 0, 1),
                ("query", 0, 2 * a),
                ("xor", 0, 1),
                ("query", 0, -a),
            )
        )
    return tuple(events)


def invoice(program, kernel=None):
    queries = [event[2] for event in program if event[0] == "query"]
    words = [address_word(k) for k in queries]
    out = {
        "ordinary_children": len(queries),
        "ordered_affine_events": sum(sum(e[0] == "affine" for e in w) for w in words),
        "aligned_xor_scans": sum(e[0] == "xor" for e in program),
        "persistent_private_rows": 0,
        "query_powers": queries,
        "child_volume_fraction_each": "1/3",
        "child_width_fraction_each": "1/3",
    }
    if kernel is not None:
        out["kernel"] = kernel
    return out


def expected_counts(indices):
    """Typed optimum formula: children 2r+c, XOR 2r (affine = 6·children)."""
    runs = consecutive_runs(indices)
    r = len(set(indices))
    c = len(runs)
    children = 2 * r + c
    return {
        "r": r,
        "c": c,
        "ordinary_children": children,
        "ordered_affine_events": 6 * children,
        "aligned_xor_scans": 2 * r,
        "baseline_ordinary_children": 3 * r,
        "baseline_ordered_affine_events": 18 * r,
        "baseline_aligned_xor_scans": 2 * r,
    }


def tapped_powers(program):
    """Prefix powers at which an XOR fires (F2 endpoint contributions)."""
    prefix = 0
    taps = []
    for event in program:
        if event[0] == "query":
            prefix += event[2]
        elif event[0] == "xor":
            taps.append(prefix)
    need(prefix == 0, "total query power must restore source layout")
    return tuple(taps)


def required_powers(indices, kernel):
    powers = []
    for j in sorted(set(indices)):
        powers.append(odd_kernel_power(j, 1, kernel))
        powers.append(odd_kernel_power(j, -1, kernel))
    return tuple(powers)


def induced_components(indices, kernel):
    """Connected components of required vertices under signed q-dyadic edges."""
    verts = set(required_powers(indices, kernel))
    # Same-sign consecutive indices join; opposite signs of equal magnitude join.
    parent = {v: v for v in verts}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for j in set(indices):
        a = odd_kernel_power(j, 1, kernel)
        union(a, -a)
    ordered = sorted(set(indices))
    for i in range(len(ordered) - 1):
        if ordered[i + 1] == ordered[i] + 1:
            for sign in (-1, 1):
                union(
                    odd_kernel_power(ordered[i], sign, kernel),
                    odd_kernel_power(ordered[i + 1], sign, kernel),
                )
    return len({find(v) for v in verts})


def q_dyadic_edge(u, v, kernel):
    return is_q_dyadic(v - u, kernel)
