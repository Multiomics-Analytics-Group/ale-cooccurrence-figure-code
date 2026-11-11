"""
Figure_S2_power_sweep.py

Pre-computes the curves Figure S2 needs and caches them in
cache/Figure_S2_power_sweep.npz, because the exact Fisher rejection-set enumeration in
power.py is O(N^2) per point and does not reach N = 1000 in reasonable time.

The speed-up is a WINDOW, not an approximation of the test. Under the alternative the
row margin R = A + B is exactly Binomial(N, f1) (a multinomial marginal), so margins
further than `nsd` standard deviations from N*f1 carry negligible probability and can
be skipped. The window does not depend on the odds ratio, so ONE rejection set per
(N, alpha, direction) serves every OR. `verify()` checks the windowed result against
the exact engine in power.py.
"""
import importlib.util, math
from pathlib import Path

import numpy as np
from scipy.special import gammaln

# Folders: ROOT is the folder above code/, and power.py sits next to this script.
ROOT = Path(__file__).resolve().parent.parent
_sp = importlib.util.spec_from_file_location("power", Path(__file__).resolve().parent / "power.py")
power = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(power)

F_REF = 0.15            # marginal frequency of each gene, held fixed as N is swept
NSD = 6.0               # margin window half-width, in binomial SDs (omitted mass < 1e-8)


def windowed_tables(N, alpha, alt, f=F_REF, nsd=NSD):
    """Every 2x2 table Fisher rejects at `alpha`, restricted to the margin window."""
    lf = power._log_factorials(N)
    mu, sd = N * f, math.sqrt(N * f * (1.0 - f))
    rlo, rhi = max(0, int(math.floor(mu - nsd * sd))), min(N, int(math.ceil(mu + nsd * sd)))
    A, B, C, D = [], [], [], []
    for r in range(rlo, rhi + 1):
        for s in range(rlo, rhi + 1):
            lo, hi = max(0, r + s - N), min(r, s)
            if hi - lo < 1:                              # <2 possible tables -> no test
                continue
            a = np.arange(lo, hi + 1)
            pmf = np.exp(lf[r] - lf[a] - lf[r - a]
                         + lf[N - r] - lf[s - a] - lf[N - r - s + a]
                         - (lf[N] - lf[s] - lf[N - s]))
            tp = pmf[::-1].cumsum()[::-1] if alt == "greater" else pmf.cumsum()
            sel = a[tp < alpha]                           # strict `<`, as in power.py
            if sel.size:
                A.append(sel); B.append(r - sel); C.append(s - sel); D.append(N - r - s + sel)
    if not A:
        return None
    a = np.concatenate(A).astype(float); b = np.concatenate(B).astype(float)
    c = np.concatenate(C).astype(float); d = np.concatenate(D).astype(float)
    base = lf[N] - gammaln(a + 1) - gammaln(b + 1) - gammaln(c + 1) - gammaln(d + 1)
    return a, b, c, d, base


def power_of(S, OR, f=F_REF):
    """Power (%) of a cached rejection set at one odds ratio."""
    if S is None:
        return 0.0
    a, b, c, d, base = S
    p = power._cells(f, f, float(OR))
    return float(np.exp(base + a * np.log(p[0]) + b * np.log(p[1])
                        + c * np.log(p[2]) + d * np.log(p[3])).sum() * 100.0)


def verify():
    """Windowed vs the exact enumeration in power.py, at sizes the exact one can reach."""
    print("verifying windowed engine against power.py")
    worst = 0.0
    for N in (40, 60, 80):
        for alpha in (0.05, 1e-4):
            for alt in ("greater", "less"):
                sig = power.rejection_tables(N, alpha, alternative=alt)
                lf = power._log_factorials(N)
                if len(sig):
                    sa, sb, sc, sd = sig[:, 0], sig[:, 1], sig[:, 2], sig[:, 3]
                    EX = (sa, sb, sc, sd, lf[N] - gammaln(sa + 1) - gammaln(sb + 1)
                          - gammaln(sc + 1) - gammaln(sd + 1))
                else:
                    EX = None
                WI = windowed_tables(N, alpha, alt)
                for OR in (20, 10, 3, 1 / 3, 0.1, 0.05):
                    e, w = power_of(EX, OR), power_of(WI, OR)
                    worst = max(worst, abs(e - w))
    print(f"   worst absolute difference over 72 cases: {worst:.3e} percentage points")
    # The residual is the truncated tail mass itself, ~1e-8 in probability at NSD = 6.
    assert worst < 1e-3, "windowed engine disagrees with the exact one"
    return worst


# --- the sweep -------------------------------------------------------------------
# Correction families: the numbers of 42C_Tenaillon's pairs testable by Fisher's exact test
# in each direction (fisher_testable_co, fisher_testable_mutex in the pair table
# data/analysis/ecoli/all_experiments/pairwise_all_methods_gene.csv), held fixed while N varies.
M_CO, M_MUTEX = 5482, 236
ALPHA = {("greater", "single"): 0.05,       ("less", "single"): 0.05,
         ("greater", "cons"):   0.05 / M_CO, ("less", "cons"):  0.05 / M_MUTEX}

N_GRID = np.unique(np.concatenate([
    np.arange(2, 251), np.arange(255, 501, 5), np.arange(510, 1001, 10)]))
# Runs all the way down to OR = 1 so the two arms meet at the null with no gap: the
# contour panel needs a continuous surface through OR = 1, where power collapses to the
# achieved size of the test. Forced to contain the round values the captions quote.
# Extra ORs are nearly free: the cost is the rejection set, built once per
# (N, alpha, direction) and reused across every OR.
OR_CO = np.unique(np.round(np.concatenate([
    np.logspace(0.0, 2.0, 60), [2, 3, 4, 5, 10, 20, 50, 100]]), 4))
OR_MX = np.round(1.0 / OR_CO, 8)[::-1]


def run(out):
    verify()
    print(f"sweeping {len(N_GRID)} sizes x 4 (direction, threshold) combinations")
    # res[f"{alt}_{reg}"] is a len(N_GRID) x len(ors) matrix
    res = {}
    for alt, ors in (("greater", OR_CO), ("less", OR_MX)):
        for reg in ("single", "cons"):
            a = ALPHA[(alt, reg)]
            Z = np.zeros((len(N_GRID), len(ors)))
            for i, N in enumerate(N_GRID):
                S = windowed_tables(int(N), a, alt)
                if S is None:
                    continue
                for j, orr in enumerate(ors):
                    Z[i, j] = power_of(S, orr)
            res[f"{alt}_{reg}"] = Z
            print(f"   done {alt:8s} {reg:6s} (alpha = {a:.3e})", flush=True)

    # Panel A: power vs N at the single reference effect, OR = 10.
    kA = {"A_co_single": ("greater", "single", 10.0), "A_co_cons": ("greater", "cons", 10.0)}
    A = {}
    for name, (alt, reg, orr) in kA.items():
        a = ALPHA[(alt, reg)]
        A[name] = np.array([power_of(windowed_tables(int(N), a, alt), orr) for N in N_GRID])
        print(f"   done panel A curve {name}", flush=True)

    np.savez_compressed(out, N_GRID=N_GRID, OR_CO=OR_CO, OR_MX=OR_MX,
                        M_CO=M_CO, M_MUTEX=M_MUTEX, F_REF=F_REF, **res, **A)
    print(f"saved -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    run(ROOT / "cache/Figure_S2_power_sweep.npz")
