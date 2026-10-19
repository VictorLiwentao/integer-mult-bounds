"""Shared harness: PR2753 LowCodes Incoming under outer-wrapper borrow fixture.

Research construction / recursive interface; no new kappa.
Prepared by Wentao Li with substantial AI assistance.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WRAPPER = REPO / "research" / "selected-outer-borrowing-wrapper"

# Odd-prime borrowed fixture inside the outer-wrapper volume bound.
Q = 3
W = 1
N = 2
K = 3
ELL = 0
STOCK = 24  # R=27, R'=48 = |GL_2(F_3)|
P = Z = T = 1
WEIGHTS = (1, 1)
LOW_DIM = 2
LOW_REQUESTS = 2
GL_ORDER = 48  # prod_(i=0)^(1) (3^2 - 3^i) = 8*6

EXPECTED_R = Q**K  # 27
EXPECTED_RPAD = ((EXPECTED_R + STOCK - 1) // STOCK) * STOCK  # 48
EXPECTED_A = Q ** (W * N)  # 9
EXPECTED_VOLUME = P * EXPECTED_R * EXPECTED_R * EXPECTED_A * EXPECTED_A  # 59049
EXPECTED_F_WIDTH = P * EXPECTED_RPAD * EXPECTED_A * EXPECTED_A * EXPECTED_R  # 104976
EXPECTED_BAD = 40824
EXPECTED_BAD_ROWS = list(range(6, EXPECTED_R))  # 21 rows
EXPECTED_GOOD_GENUINE = list(range(0, 6))
EXPECTED_BAD_PER_ROW = EXPECTED_BAD // len(EXPECTED_BAD_ROWS)  # 1944


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def install_wrapper():
    """Authenticate PR2786/PR2753 export used by the outer borrowing wrapper."""
    if str(WRAPPER) not in sys.path:
        sys.path.insert(0, str(WRAPPER))
    import predecessor

    return predecessor.installed()


def decode_count(count):
    return sum(bit << i for i, bit in enumerate(count.tape.cells[1:]) if bit in (0, 1))


def plan_pad(rows, stock):
    return ((rows + stock - 1) // stock) * stock


def gl2_order(q: int = Q, dim: int = LOW_DIM) -> int:
    """|GL_dim(F_q)| = prod_(i=0)^(dim-1) (q^dim - q^i)."""
    order = 1
    for i in range(dim):
        order *= q**dim - q**i
    return order


def three_power_never_divisible_by_16(max_k: int = 64) -> list[int]:
    """Return 3^k mod 16 for k=0..max_k; none are 0."""
    out = []
    value = 1
    for _ in range(max_k + 1):
        out.append(value % 16)
        value = (value * 3) % 16
    return out


def census_call(padded, rows, returned, destination, n=N, m=Q**W, r=EXPECTED_R):
    """Count F_I origin mismatches and support them by row index."""
    rows_v = decode_count(rows)
    j = Q**ELL
    a = EXPECTED_A
    width = P * rows_v * a * a * j * j * Z * r * T
    gap = j * Z * r
    suffix = j * T
    bad = 0
    bad_rows: dict[int, int] = {}
    for address in range(width):
        target = destination(address, n, m, WEIGHTS, gap, suffix)
        ok = returned.origins.get(target + 1) == padded.origins.get(address + 1)
        # outer = row when P=1
        addr, _s = divmod(address, suffix)
        addr, _tail = divmod(addr, a)
        addr, _g = divmod(addr, gap)
        row, _head = divmod(addr, a)
        if not ok:
            bad += 1
            bad_rows[row] = bad_rows.get(row, 0) + 1
    return {
        "rows": rows_v,
        "width": width,
        "bad": bad,
        "bad_rows": sorted(bad_rows),
        "bad_per_row": dict(sorted(bad_rows.items())),
        "good_genuine": [row for row in range(r) if row not in bad_rows],
        "pad_rows_bad": sum(1 for row in bad_rows if row >= r),
    }


def run_model_callee():
    """Outer-wrapper interchange at the odd-prime borrow fixture with model_callee."""
    with install_wrapper():
        import checks

        return checks.case(
            q=Q, w=W, n=N, k=K, ell=ELL, stock_value=STOCK
        )


def run_incoming_census():
    """Incoming LowCodes callee under the same fixture; return per-call censuses.

    The wrapper endpoint check is expected to reject; censuses are taken inside
    the callee before that rejection.
    """
    with install_wrapper():
        from cardinal_counts import Count
        from check_nested_model import Catalogue, Topology
        from check_runtime import destination
        from directory import Context
        from low_codes import LowCodes
        import model
        from model import Consumer, Incoming
        from node import Node
        from records import Tape
        from words import Arena, Ring
        import checks

        arena, indices = Arena(3), Arena(8)
        modulus = arena.input(Q)
        ring = Ring(modulus)
        catalogue = Catalogue()
        catalogue.requests = tuple(
            model.Request("MOVE", i, 0) for i in range(LOW_REQUESTS)
        )
        catalogue.codes = LowCodes(Q, LOW_DIM, LOW_REQUESTS)
        need(catalogue.codes.size == GL_ORDER, "LowCodes size equals |GL2(F3)|")
        context = Context(ring, catalogue.codes)
        size, depth = indices.input(2), indices.input(0)
        incoming = Incoming(context, indices, WEIGHTS)
        consumer = Consumer(
            context, indices, object(), size, depth, catalogue, incoming
        )
        node = Node(
            context,
            indices,
            object(),
            size,
            depth,
            Topology(catalogue),
            consumer,
            incoming,
        )
        old, one = Tape(), Count.literal(1)
        censuses = []

        def factory(padded, rows):
            g = Count.literal(EXPECTED_R)
            b = Count.literal(1)
            s = Count.literal(1)
            try:
                returned = node.run(padded, old, one, rows, b, g, s)
            finally:
                g.close()
                b.close()
                s.close()
            censuses.append(census_call(padded, rows, returned, destination))
            return returned

        case_error = None
        try:
            checks.case(
                q=Q,
                w=W,
                n=N,
                k=K,
                ell=ELL,
                stock_value=STOCK,
                callee_factory=factory,
            )
        except ValueError as error:
            case_error = str(error)
            # checks.case may surface fixture teardown after the endpoint reject.
            if (
                "row-pointwise endpoint" not in case_error
                and "teardown" not in case_error
            ):
                raise
        finally:
            old.clear()
            one.close()
            incoming.close()

        need(len(censuses) >= 1, "at least one F call census")
        endpoint_rejected = any(c["bad"] == EXPECTED_BAD for c in censuses)
        need(endpoint_rejected, "Incoming F_I mismatches match expected census")
        return {
            "censuses": censuses,
            "endpoint_rejected": True,
            "case_error": case_error,
            "residuals": dict(consumer.calls),
            "children": dict(consumer.children),
            "gl_order": catalogue.codes.size,
        }
