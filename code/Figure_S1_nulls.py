"""
Figure_S1_nulls.py  (run in the pipeline's environment, which contains DISCOVER)

Caches what Figure S1 needs for one real pair, glmS-rho in 42C_Tenaillon,
so Figure_S1.ipynb itself runs in environment B. Same split as
Figure_S2_power_sweep.py -> Figure_S2.ipynb.

Both nulls are rebuilt exactly as analysis_pipeline/src/pairwise_tests.py of the pipeline
repository builds them:
  Fisher    hypergeometric on the observed counts
  DISCOVER  background fitted on the FULL experiment matrix (all genes), then
            q_j = p_Aj * p_Bj per endpoint, with structurally forced overlaps set to 1,
            and the overlap distributed as Poisson-binomial over the q_j
The script refuses to write the cache unless every p_min it computes matches the value the
pipeline stored in pairwise_all_methods_gene.csv.

usage, from the folder that holds code/, data/ and cache/, in the pipeline's container image
(built from the docker/ folder of the pipeline repository, ale-cooccurrence-mutual-exclusivity-nf,
whose README also shows how to make the same environment with conda):
  docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" -w /work -e KMP_DUPLICATE_LIB_OK=TRUE \
      ale-cooccurrence:dev python code/Figure_S1_nulls.py
"""
from pathlib import Path

import discover
import numpy as np
import pandas as pd
from scipy.stats import hypergeom

ROOT = Path(__file__).resolve().parent.parent
GENE_A, GENE_B = "rho", "glmS"
EXP_PREFIX = "42C_Tenaillon"
OUT = ROOT / "cache/Figure_S1_nulls.npz"

mat_dir = next(p for p in (ROOT / "data/analysis/ecoli/matrices/gene").iterdir()
               if p.name.startswith(EXP_PREFIX))
M = pd.read_csv(mat_dir / "matrix.csv", index_col=0)
M.columns = M.columns.astype(str)
N = M.shape[1]

ev = discover.DiscoverMatrix(M)          # fitted on the full matrix (its optimizer prints a log)
bg = pd.DataFrame(ev.bg, index=ev.rownames, columns=ev.colnames)

full = M.values.astype(bool)
const = {u: bool(full[i].all()) for i, u in enumerate(M.index)}
saturated = full.all(axis=0)

a, b = M.loc[GENE_A].values.astype(bool), M.loc[GENE_B].values.astype(bool)
cA, cB, obs = int(a.sum()), int(b.sum()), int((a & b).sum())

# ---- Fisher: hypergeometric, support max(0, cA+cB-N) .. min(cA, cB) ---------------------
k_f = np.arange(0, min(cA, cB) + 1)
pmf_fisher = hypergeom.pmf(k_f, N, cA, cB)
fisher_xmin, fisher_xmax = max(0, cA + cB - N), min(cA, cB)
fisher_pmin_me = float(hypergeom.cdf(fisher_xmin, N, cA, cB))
fisher_pmin_co = float(hypergeom.sf(fisher_xmax - 1, N, cA, cB))

# ---- DISCOVER: Poisson-binomial over q_j, support #{q_j = 1} .. N - #{q_j = 0} -----------
qj = bg.loc[GENE_A].values * bg.loc[GENE_B].values
forced = ((np.full(qj.shape, const[GENE_A]) | saturated)
          & (np.full(qj.shape, const[GENE_B]) | saturated))
qj = np.where(forced, 1.0, np.clip(qj, 1e-15, 1 - 1e-15))
pmf_discover = np.array([1.0])
for q in qj:
    pmf_discover = np.convolve(pmf_discover, [1.0 - q, q])
discover_xmin, discover_xmax = int((qj == 1.0).sum()), int(N - (qj == 0.0).sum())
log_pmin_me = float(np.log1p(-qj[qj < 1.0]).sum())
log_pmin_co = float(np.log(qj[qj > 0.0]).sum())

# ---- refuse to cache anything that disagrees with the pipeline ---------------------------
P = pd.read_csv(ROOT / "data/analysis/ecoli/all_experiments/pairwise_all_methods_gene.csv",
                low_memory=False)
row = P[P.exp.astype(str).str.startswith(EXP_PREFIX)
        & (((P.unit1 == GENE_A) & (P.unit2 == GENE_B))
           | ((P.unit1 == GENE_B) & (P.unit2 == GENE_A)))].iloc[0]
checks = {"fisher_floor_mutex": fisher_pmin_me, "fisher_floor_co": fisher_pmin_co,
          "discover_floor_mutex": float(np.exp(log_pmin_me)),
          "discover_floor_co": float(np.exp(log_pmin_co))}
for col, mine in checks.items():
    assert np.isclose(mine, float(row[col]), rtol=1e-6, atol=0), f"{col}: {mine} vs {row[col]}"
assert np.isclose(pmf_discover[0], np.exp(log_pmin_me), rtol=1e-9)   # P(X = 0) is p_min here

# endpoint order for the observed-data strip: A only, B only, neither (no endpoint has both)
order = np.r_[np.where(a & ~b)[0], np.where(~a & b)[0], np.where(a & b)[0], np.where(~a & ~b)[0]]

OUT.parent.mkdir(parents=True, exist_ok=True)
np.savez_compressed(
    OUT, gene_a=GENE_A, gene_b=GENE_B, N=N, count_a=cA, count_b=cB, observed=obs,
    row_a=a[order], row_b=b[order],
    pmf_fisher=pmf_fisher, pmf_discover=pmf_discover,
    fisher_xmin=fisher_xmin, fisher_xmax=fisher_xmax,
    fisher_pmin_me=fisher_pmin_me, fisher_pmin_co=fisher_pmin_co,
    discover_xmin=discover_xmin, discover_xmax=discover_xmax,
    discover_log_pmin_me=log_pmin_me, discover_log_pmin_co=log_pmin_co)

print(f"{GENE_B}-{GENE_A} in {EXP_PREFIX}: N = {N}, {GENE_A} {cA}, {GENE_B} {cB}, overlap {obs}")
print(f"  Fisher    ME extreme {fisher_xmin:>3}  p_min {fisher_pmin_me:.4g}   "
      f"CO extreme {fisher_xmax:>3}  p_min {fisher_pmin_co:.4g}")
print(f"  DISCOVER  ME extreme {discover_xmin:>3}  p_min {np.exp(log_pmin_me):.4g}   "
      f"CO extreme {discover_xmax:>3}  p_min {np.exp(log_pmin_co):.4g}")
print(f"  all four p_min match the pipeline -> {OUT.relative_to(ROOT)}")
