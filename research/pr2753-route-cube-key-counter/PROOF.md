# Exact non-fibre key and Counter work of PR2753 `routes.route_cube`

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.

This prices non-fibre sites on the reached owner-route primitive
`routes.route_cube` from David Arias's PR2753 head
`7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`, as retained byte-exactly under
`research/selected-bit-recursive-caller/predecessor/vendor/` on pin
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. It answers the first step of
open question 1 of [#3944](https://github.com/CrocSwap/integer-mult-bounds/pull/3944)
(fibre invoice): meter `append_word`, key paths and partition Counter
lifetimes on the same fixtures. Jose Manuel's PR2697/PR2809 supply the vendor
lineage. The routine and its dependencies are unchanged. No new κ, supplier
admission or H2 replacement is claimed. The selected decimal remains
`0.001672660197076918`.

This package does **not** reprint the #3944 fibre `copy_bits` identity
`(2 d² L + 2) V`. Numerical `Matrices`/`high_key` Ring traffic and physical
pool acquisition remain open.

## Domain and metric

Fix an odd prime label `q >= 3`, atom exponent `w >= 1`, dimension `d >= 1`
and fibre length `F >= 1`. Write `M = q^w`, `L = bit_length(M) + 1`,
`cap = M/q`, `H = cap^(d²)`, and `coords = d²`. When `cap > 1` put
`P = coords · L`; when `cap = 1` put `P = 0`.

The metric counts only:

1. successful `records.append_word` **tape cells written** during decoration,
2. `records.read_word` **calls** during key stripping,
3. `routes.high_key` **calls**,
4. `routes.copy_key` **tape cells written** inside `partition`,
5. partition-local `stream.Counter` constructors, decrements and closes
   (the `Counter` name bound inside `routes.py`, not Counters inside
   `bitstream.copy_bits`).

Fibre `copy_bits` writes, blank tests and Python wall-clock time are excluded.

## Word-width lemma

Every Arena Word used as a route key digit is allocated at width `arena.bits = L`
with payload cells `[0]^{L}` followed by `RIGHT`. `append_word` copies until
`RIGHT` then appends one `WORD_END`, so each digit contributes exactly
`L + 1` tape cells. Independent fixtures with `L ∈ {3,5,6,8}` confirm the
payload width.

## Decoration and stripping

`route_cube` walks the high odometer once for decoration: for each of the `H`
highs it calls `high_key` once and `append_word` once per coordinate digit.
Hence

```text
high_key calls          = H,
append_word calls       = H · coords,
append_word cells       = H · coords · (L + 1).
```

Key stripping walks the odometer again and calls `read_word` once per digit:

```text
read_word calls         = H · coords.
```

These identities do not involve the fibre length `F`. Fixtures with the same
`(q,w,d)` and distinct `F` share identical `append_word` cell totals, so the
closed form is not forced by any fibre-volume formula linear in `V = H F`.

## Partition key copy and Counter census

When `cap = 1` the source skips the partition block, so `P = 0` and every
partition meter below is zero.

When `cap > 1`, each of the `coords` coordinates runs an `L`-step one-hot
cursor (same cursor walk as in #3944's structural lemma, used here only to
count partition calls). Each `partition` call, for every one of the `H`
records, executes `copy_key` once into a bucket and once out to the merged
output. Keys have `coords` words of `L + 1` cells each. Thus

```text
copy_key calls          = 2 · H · P,
copy_key cells          = 2 · H · P · coords · (L + 1).
```

Each partition constructs one `Counter(context.highs)` and two
`Counter(count)` drain objects (one per bucket), closes all three, and
performs exactly `H` decrements on the records Counter plus `H` decrements
across the two bucket Counters. Hence

```text
Counter constructors    = 3 · P,
Counter decrements      = 2 · H · P,
Counter closes          = 3 · P.
```

## Exact invoice (summary)

| Meter | `cap > 1` | `cap = 1` |
| --- | ---: | ---: |
| `high_key` calls | `H` | `H` |
| `append_word` calls | `H · d²` | `H · d²` |
| `append_word` cells | `H · d² · (L+1)` | `H · d² · (L+1)` |
| `read_word` calls | `H · d²` | `H · d²` |
| `copy_key` cells | `2 H P d² (L+1)` | `0` |
| Counter ctors/closes | `3 P` | `0` |
| Counter decrements | `2 H P` | `0` |

with `P = d² L`. All identities are checked on six fixtures, including a
non-identity scaled chart, `d = 2`, `q = 5`, and the `w = 1` (`cap = 1`)
control.

## Scope limits

- Does not invoice numerical `high_key` / `Matrices` Ring traffic.
- Does not invoice fibre `copy_bits` and does not restate `(2 d² L + 2) V`.
- Does not claim that this non-fibre bill alone replaces an `Ω(wV)` route
  lower bound; fibre payload copies remain the dominant `V`-linear term for
  large `F`.
- Does not admit a supplier, change kappa, or price an H2 replacement.
