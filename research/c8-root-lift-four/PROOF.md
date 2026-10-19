# Four C8 involution outputs still need four calls

## Statement

Let \(C_8=\langle g\mid g^8=e\rangle\) and write \(\varepsilon=[g]+[e]\) in characteristic two, so
\[
  \mathbb F_2[C_8]\cong\mathbb F_2[\varepsilon]/(\varepsilon^8),\qquad [g^4]+[e]=\varepsilon^4.
\]
On four registers a paid factor is
\[
  D_N([g^s])=I+([g^s]+[e])N,\qquad s\in\{1,\ldots,7\},
\]
where \(N=xy^T\in M_4(\mathbb F_2)\) is a rank-one idempotent (\(x,y\neq 0\), \(y^Tx=1\)). There are 120 such matrices. The target
\[
  \tau=I+\varepsilon^4 I_4=\operatorname{diag}([g^4],[g^4],[g^4],[g^4])
\]
has exact minimum four. The diagonal word \(\prod_{i=1}^4(I+\varepsilon^4 E_{ii})\) attains four because \(\varepsilon^8=0\) kills every cross term. No word of length at most three equals \(\tau\).

Multiplication by \(\varepsilon\) on the group algebra has rank 7, and multiplication by \(\varepsilon^4\) has rank 4. Three order-eight labels therefore have rank budget 21 against four involution blocks of total rank 16. The length-three candidate is not ruled out by that screen.

No new kappa is claimed. The model has no rational frames, hosting, restoration, or supplier conversion.

## Leading forms

Every odd exponent has increment \(\varepsilon\) plus higher terms. Every even exponent has valuation at least 2. In a product \(\prod(I+A_j)\), the degree-1 part of the product minus \(I\) is the sum of the degree-1 parts, because every product of two or more increments has valuation at least 2. For \(\tau\) that degree-1 coefficient is zero, so the idempotents on the odd labels sum to zero.

If every label is even, each increment lies in \((\varepsilon^2)\) and every product of two increments lies in \((\varepsilon^4)\). The coefficients of \(\varepsilon^2\) and \(\varepsilon^3\) are therefore sums of the individual coefficients. The even increments are
\[
\begin{align*}
[g^2]+[e]&=\varepsilon^2,\\
[g^4]+[e]&=\varepsilon^4,\\
[g^6]+[e]&=\varepsilon^2+\varepsilon^4+\varepsilon^6.
\end{align*}
\]
None contains \(\varepsilon^3\). The coefficient of \(\varepsilon^2\) is the sum of the idempotents on labels in \(\{2,6\}\).

## Rank-one sums

A single rank-one idempotent is not zero. A sum of three is zero only if one equals the sum of the other two. That never happens. If \(N=xy^T\) and \(M=uv^T\) are rank-one idempotents and \(x=u\) or \(y=v\), then \((N+M)^2=0\): the shared image (respectively shared row) makes the scalar \((y+v)\cdot x\) or \(y\cdot(x+u)\) equal to \(1+1=0\). If \(x\neq u\) and \(y\neq v\), those two nonzero vectors are linearly independent over \(\mathbb F_2\), and \(N+M\) has rank 2. Either way \(N+M\) is not a nonzero rank-one idempotent. The checker confirms both halves on all \(120^2\) pairs: 0 sums land back in the rank-one set, and every sum of rank at most 1 squares to zero.

Consequently one odd label, or three odd labels, cannot cancel degree 1. Two odd labels cancel degree 1 only when they carry the same idempotent.

## The 399 patterns

There are \(7+49+343=399\) ordered label words of length 1, 2, and 3. Expand each word in the free algebra on idempotent letters, imposing only \(N^2=N\) by deleting adjacent repetitions. While a coefficient of \(\varepsilon\), \(\varepsilon^2\), or \(\varepsilon^3\) is a sum of exactly two letters, replace one letter by the other and continue. The checker performs that reduction and finds only three outcomes:

- 228 patterns die on a single surviving letter in degree 1, 2, or 3. A rank-one idempotent is not zero.
- 72 patterns die on a sum of three letters in one of those degrees. The lemma above says that sum is not zero.
- 99 patterns cancel every degree below 4, and the degree-4 coefficient that remains is a sum of at most three letters.

A sum of at most three rank-one matrices has rank at most 3, so it is not \(I_4\). For the all-even words the same run checks that the degree-2 coefficient really is the \(\{2,6\}\) letter sum and that degree 3 is empty, which is the cross-term claim above. No pattern is left unclassified.

The four axis factors \(I+\varepsilon^4 E_{ii}\) multiply to \(\tau\). The minimum is exactly four.

## What the reduction is not

The same alphabet on \(C_4\), with target degree 2, is the earlier root-lift obstruction. Degree 4 is a different associated-graded piece: labels of valuation 1 exist, and their pairwise products land on the target degree. This note does not treat \(C_{16}\), a noncommutative group algebra, or any register count other than four.
