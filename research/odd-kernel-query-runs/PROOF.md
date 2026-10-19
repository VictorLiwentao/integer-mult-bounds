# Odd-kernel run batching for completed native DATA shears

This is a local recursive-interface construction and a scoped optimum in an
explicitly restricted alphabet. Ordinary ADDRESS interchange remains a premise.
There is no new supplier, kappa, or formal multiplication proof.

It combines the dyadic-run schedule of
[PR953](https://github.com/CrocSwap/integer-mult-bounds/pull/953)
(`research/dyadic-query-runs`) with the odd-kernel admission pattern of
[#2687](https://github.com/CrocSwap/integer-mult-bounds/pull/2687)
(`research/odd-kernel-query-pair`), itself the general-`q` form of
[PR840](https://github.com/CrocSwap/integer-mult-bounds/pull/840).

## Object

Use the same six ADDRESS fields and unipotent push `h` as PR521/PR840:

```text
s=(1,0,1,-1,0,-1)^T, r=(1,0,-1,-1,0,1)^T,
M(k)=I6+(k/4)s r^T,   h = array permutation of M(1).
```

For a positive odd kernel `q` and a finite nonempty index set
`J ⊂ ℤ_{≥0}`, the completed batch endpoint is

```text
D_{q,J}(x,y,z)=(x + Σ_{j∈J}(h^(q·2^j)+h^(-q·2^j)) y, y, z).
```

The optimization alphabet admits only queries whose power is a nonzero
**signed q-dyadic** integer `±q·2^k` (`k≥0`), together with aligned source
XORs on the exclusive target. Role mixing, queries on the source, and
modulus-specific shortcuts are outside the alphabet.

## Run walk

For a consecutive interval `[ℓ,u]` write the cumulative-power tour

```text
0, -q·2^u, …, -q·2^ℓ, +q·2^ℓ, …, +q·2^u, 0.
```

Execute `Q(next−current)` on each edge and an XOR at every nonzero listed
vertex. Every edge difference is signed q-dyadic: the exterior edges are
`±q·2^u`, each same-sign interior gap is `±q·2^j`, and the middle crossing
is `q·2^{ℓ+1}`. If the interval has `t` indices there are `2t+1` queries and
`2t` XOR scans. Concatenate over the `c` maximal consecutive runs of `J`.
With `r=|J|` the complete word uses

```text
children = 2r+c,   affine events = 6(2r+c),   XOR scans = 2r.
```

The baseline concatenates one #2687/#840 fused pair per index, costing
`3r` children, `18r` affine events and the same `2r` XOR scans. The saving
is `r−c` full queries. Total query power is zero, so the source layout is
restored; each XOR at prefix `p` contributes the required `h^{-p}` term.

## Admission

Each query power `k` has odd part dividing `q` in its ADDRESS diagonal and
control denominators (inherited from #2687). Therefore the lowering
specializes to every **odd modulus coprime to `q`**. Even moduli and odd
moduli sharing a prime with `q` are excluded. When `q=1` this recovers the
all-odd-radix claim of dyadic-query-runs.

## Restricted-alphabet lower bound

On a full-order odd orbit the ADDRESS action is Laurent. Restoring arbitrary
`x` forces total integer query power zero. Required tap vertices are
`S={±q·2^j : j∈J}`; each must be visited oddly, so at least `2r` XORs occur.

Join two distinct elements of `S` when their difference is signed q-dyadic.
Same-sign vertices join exactly on consecutive indices; opposite signs of
equal magnitude join; opposite signs of unequal magnitude never join (the
sum has an odd factor larger than one times `q`). The induced graph therefore
has exactly `c` components — the consecutive runs of `J`.

Any closed walk with `q` edges, written cyclically by its first `q` vertices,
has `a` visits in `S` and `b` visits outside `S`, so `q=a+b` and `a≥2r`.
The walk starts at `0∉S`, hence `b≥1`. Each block of `S` vertices between
outside occurrences lies in one component, and all `c` components must be
visited, so `b≥c`. Thus `q≥2r+c`. The run walk attains the bound.

Typed counts are independent of `q`. No odd kernel improves the invoice over
the dyadic (`q=1`) case; larger radical(`q`) only shrinks the admitted modulus
set.

## Evidence boundary

The checker verifies, for kernels `{1,3,5,7,9,15}` and every nonempty
`J⊆{0,…,5}` (63 sets), that batch/baseline invoices match the formulas, that
tapped powers equal `S`, that induced components equal `c`, that every edge
is q-dyadic, and that closed-form admission matches denominator invertibility
on a fixed probe modulus set. Rational and modular columns check the inherited
ADDRESS lowering. An independent module rebuilds the seed walk and pattern
without importing `verify.py`. No supplier hosting, precision/dispatch bill,
or new kappa is claimed.
