"""
power.py

Exact power engine for the one-sided Fisher exact test, used only by the Figure S2
power sweep (Figure_S2_power_sweep.py).

Power is the probability that Fisher's exact test WOULD call a pair significant IF a
real interaction of a PRE-SPECIFIED effect size (odds ratio) existed, given the
number of lineages N, the two marginal frequencies and the threshold alpha. Each
direction is one-sided, as in the main analysis: co-occurrence (OR > 1) and mutual
exclusivity (OR < 1).

Method ("fast exact"):
  power(pair, OR) = sum, over every 2x2 table Fisher would reject, of that table's
  multinomial probability under (f1, f2, OR). Whether a table is rejected depends
  only on its margins, N and alpha, NOT on OR or on the pair, so the rejection
  set is computed ONCE per (N, alpha) and reused for every pair and every OR. This
  is EXACT.
"""
import math
from functools import lru_cache

import numpy as np
from scipy.special import gammaln


@lru_cache(maxsize=256)
def _log_factorials(N):
    """lf[k] = log(k!) for k = 0..N."""
    return gammaln(np.arange(N + 1) + 1)


def _cells(f1, f2, orr):
    """Four multinomial cell probabilities (both, A-only, B-only, neither) for
    marginal frequencies f1, f2 and odds ratio `orr` (the standard 2x2 construction)."""
    if orr == 1:
        p11 = f1 * f2
    else:
        a = orr - 1.0
        b = 1.0 - (f1 + f2) + orr * (f1 + f2)
        c = orr * f1 * f2
        p11 = (b - math.sqrt(max(b * b - 4 * a * c, 0.0))) / (2 * a)
    return np.clip(np.array([p11, f1 - p11, f2 - p11, 1.0 - f1 - f2 + p11]), 1e-15, None)


def rejection_tables(N, alpha, alternative="greater"):
    """All 2x2 tables (a, b, c, d) summing to N that Fisher's exact test REJECTS at `alpha`.

    `alternative` matches the MAIN ANALYSIS, which tests each direction one-sided:
      "greater"   co-occurrence      p = P(X >= a)   (hypergeometric upper tail)
      "less"      mutual exclusivity p = P(X <= a)   (hypergeometric lower tail)
      "two-sided" the sum-of-smaller-probabilities rule (not used by Figure S2).
    Depends only on (N, alpha, alternative), so it is computed once and reused for every
    pair and every OR. Returns a (K, 4) float array."""
    lf = _log_factorials(N)
    A, B, C, D = [], [], [], []
    for r in range(N + 1):
        for s in range(N + 1):
            lo = max(0, r + s - N)
            hi = min(r, s)
            if hi - lo < 1:                          # <2 possible tables -> no test
                continue
            a = np.arange(lo, hi + 1)
            logpmf = (lf[r] - lf[a] - lf[r - a]
                      + lf[N - r] - lf[s - a] - lf[N - r - s + a]
                      - (lf[N] - lf[s] - lf[N - s]))
            pmf = np.exp(logpmf)
            if alternative == "greater":
                tp = pmf[::-1].cumsum()[::-1]                 # P(X >= a), one-sided upper
            elif alternative == "less":
                tp = pmf.cumsum()                             # P(X <= a), one-sided lower
            else:
                order = np.argsort(pmf, kind="mergesort")
                sp = pmf[order]
                cs = np.cumsum(sp)
                tp = cs[np.searchsorted(sp, pmf + 1e-12, side="right") - 1]
            # Strict `<`, as in the pipeline, which compares the q-value (significance) and
            # the smallest attainable p-value (testability) with `< significance_threshold`.
            # With a discrete test the boundary can be hit exactly, so the direction of the
            # comparison is a real convention rather than a formality.
            for ai in a[tp < alpha]:
                A.append(ai); B.append(r - ai); C.append(s - ai); D.append(N - r - s + ai)
    if not A:
        return np.empty((0, 4), dtype=float)
    return np.column_stack([A, B, C, D]).astype(float)
