# Exact key/Counter invoice for PR2753 `route_cube` (non-fibre)

**Partial, conditional implementation bill. No new supplier, kappa, or H2 admission.**

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.

## Result

On the pinned PR2753 owner-route primitive `routes.route_cube` (vendor bytes
unchanged from head `7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`), non-fibre
key and partition-Counter work is exactly

| Meter | `cap > 1` | `cap = 1` |
| --- | ---: | ---: |
| `append_word` cells | `H · d² · (L+1)` | `H · d² · (L+1)` |
| `high_key` / `read_word` calls | `H` / `H · d²` | `H` / `H · d²` |
| `copy_key` cells | `2 H P d² (L+1)` | `0` |
| Counter ctors / decrements | `3 P` / `2 H P` | `0` / `0` |

with `M = q^w`, `L = bit_length(M)+1`, `cap = M/q`, `H = cap^(d²)`,
`P = d² L` when `cap > 1` else `0`. See [PROOF.md](PROOF.md).

This answers open question 1 of [#3944](https://github.com/CrocSwap/integer-mult-bounds/pull/3944)
at the stated first step: meter `append_word` and Counter lifetimes on the
same fixtures. The `append_word` identity is independent of fibre length `F`
and is **not** forced by the fibre formula `(2 d² L + 2) V` (which this
package does not reprint). Numerical `high_key` Ring traffic and pool
acquisition remain open. Selected decimal stays `0.001672660197076918`.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/pr2753-route-cube-key-counter --check-only
python3.12 -B scripts/research_package.py --package research/pr2753-route-cube-key-counter
```

Direct gates (including `-O` via `need()`):

```sh
python3.12 -I -B research/pr2753-route-cube-key-counter/verify.py
python3.12 -I -O -B research/pr2753-route-cube-key-counter/verify.py
python3.12 -I -B research/pr2753-route-cube-key-counter/independent.py
python3.12 -I -B research/pr2753-route-cube-key-counter/test_package.py
```

Expected: `PASS_PR2753_ROUTE_CUBE_KEY_COUNTER`,
`PASS_INDEPENDENT_PR2753_ROUTE_CUBE_KEY_COUNTER`,
`PASS_PR2753_ROUTE_CUBE_KEY_COUNTER_PACKAGE_TESTS`.

## Soft overlap

| Predecessor | Difference |
| --- | --- |
| `pr2753-route-cube-owv-fibre` (#3944) | Fibre `copy_bits` only; this package meters key/Counter sites and refuses to reprint the fibre formula. |
| `linear-sign-total-traffic` | Sign only; leaves route/leaf binding open. |
| `selected-route-live-volume` | Storage peaks, not key/Counter time. |
| `binary-digit-cost-audit` | Digit/`atom_swap` bills; not `route_cube`. |

Estimated soft overlap ≈ 0.40 (complementary non-fibre invoice on the same
pinned primitive; answers #3944 OQ1 first step without retargeting fibre).

## Open next questions

1. Can numerical `Matrices`/`high_key` Ring traffic be closed in the same
   all-parameter style as `linear-sign-total-traffic`'s countdown lemma?
2. Does composing fibre + key + Counter + numerical traffic yield a single
   total-tape identity that sharpens bootstrap constants beyond fibre alone?

## Credit

David Arias (PR2753) stated the `O(wV)` route/leaf baseline and supplied the
recursive caller. Jose Manuel (PR2697/PR2809) supplies the routes/bitstream
lineage and physical caller. Nick Petalas (PR2708) proved route live-volume
storage for the same decorated cube. Arham Tahir (`linear-sign-total-traffic`)
closed the linear-sign traffic and recorded the route/leaf follow-up. The
[#3944](https://github.com/CrocSwap/integer-mult-bounds/pull/3944) fibre
invoice posed the total-traffic open question answered here at the key/Counter
first step. This package adds only the exact non-fibre key and partition-Counter
identities on pinned `route_cube`.
