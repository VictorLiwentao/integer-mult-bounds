# Proof: scale-normalization of P_(2,1) on (Z/3Z)^2

**Scoped interface construction; no new kappa.**

## Setup

Let `G = (Z/3Z)^2` and `a = (2,1)`. The weighted reversal

```text
(P x)_i = a_i x_{1-i}
```

gives `P(x0,x1) = (2 x1, x0)`. Then `P(P(x)) = (2 x0, 2 x1) = 2x`, so
`P^2 = 2 I ≠ I`. By Theorem 1 of `weighted-wrapper-contract`, the ordinary
two-call body

```text
D -= H; F_P; D += H; F_Q; D = -D; D += H
```

equals the interchange `J(H,D)=(D,H)` on all of `G×G` if and only if
`P^2=I` and `Q=P`. Equal calls with this `P` therefore fail. Formula (5) of
that package counts exactly

```text
3^2 · gcd(3,2·1-1) · gcd(3,1·2-1) = 9
```

correct address pairs out of 81.

## Normalization

Let `T = diag(1,2)` and `P' = T P`. Explicitly

```text
P'(x0,x1) = (2 x1, 2 x0).
```

Then `P'(P'(x)) = x`, so `(P')^2 = I` and `(P')^{-1} = P'`. Define the
unnormalized callee `F_a(H,D) = (P D, P^{-1} H)` and the output post-scales

```text
Norm(H',D') = ( (H'_0, 2 H'_1), (2 D'_0, D'_1) ).
```

A direct expansion gives

```text
Norm(F_a(H,D)) = (P' D, P' H) = F_{P'}(H,D).
```

Thus each wrapper call may keep the proposed weight table `a=(2,1)` and apply
exactly two constant modular multiplies on the callee outputs.

## Wrapper admission

Substitute `F = Norm ∘ F_a` for both calls. Then both one-bank maps equal the
involutory `P'`, so Theorem 1 applies and the word equals `J` on all 81
address pairs. The executable census in `normalize.py` confirms
`81/81` agreements; three wrong-scale controls remain imperfect.

## Exact bill

Let `V = |G| = 9`. Each `Norm` touches one H-coordinate and one D-coordinate
across the address volume, costing `2V` modular multiplies by the constant 2.
Two wrapper calls cost

```text
scales_two_F = 4 V = 36.
```

No input restoration is required (scales act on callee outputs only). No
weight-table rewrite is claimed: the proposed callee stays `(2,1)`.

## Limitations

This prices one concrete algebraic callee on `G=(Z/3Z)^2`. It does not admit
a BIT supplier, change the selected κ, implement a physical tape inventory, or
bind PR2753 Incoming / outer-borrowing `F_I`. Changing the wrapper word would
require a separate proof.
