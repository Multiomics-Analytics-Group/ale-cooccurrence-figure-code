# Figure code for the ALE co-occurrence and mutual exclusivity article

This folder holds the code that draws the figures of the article

> A statistical framework for identifying candidate genetic interactions from adaptive laboratory
> evolution data.
> Binhuan Sun, Adam M. Feist, Patrick V. Phaneuf, Alberto Santos.

The figures are drawn from the outputs of the analysis pipeline
[ale-cooccurrence-mutual-exclusivity-nf](https://github.com/Multiomics-Analytics-Group/ale-cooccurrence-mutual-exclusivity-nf).
The pipeline outputs that the figures read are included in `data/` (for four experiments, only what
the figures use, see [Data](#data)), so the figures can be rebuilt without running the pipeline.

## Contents

```
code/           one notebook or script per figure, two scripts that compute the files in cache/,
                and two helpers (power.py, svg_for_illustrator.py)
data/           copies of the pipeline outputs the figures read, and, for four experiments whose
                mutation data are not public, only what the figures use
cache/          precomputed values for Figures S1 and S2
environments/   the two conda environments
figures/        the files the code writes, one folder per figure
run_all.sh      rebuilds every figure
```

`data/`, `cache/` and `figures/` each hold an `MD5SUMS` file that lists the checksums of their files
(the PNG files only, for `figures/`). All three are checked from this folder, as shown below.

## Figures

| Figure | Code | Reads | Writes in `figures/` | Environment |
|---|---|---|---|---|
| 1 | `code/Figure_1.ipynb` | `qc_mutations.tsv`, `nonpublic/gene_by_endpoint.tsv`, `nonpublic/endpoints.tsv`, `nonpublic/mutation_types.tsv`, `qc_pipeline_report.tsv`, `02_select_species_summary.json` | `Figure_1/Figure_1` | A |
| 2 | none | | | |
| 3 | `code/Figure_3.ipynb` | `qc_mutations.tsv`, `nonpublic/gene_by_endpoint.tsv`, `pairwise_all_methods_gene.csv` | `Figure_3/Figure_3` | A |
| 4 | `code/Figure_4.ipynb` | `pairwise_all_methods_gene.csv`, `qc_mutations.tsv`, `nonpublic/gene_by_endpoint.tsv`, `nonpublic/distinct_mutations.tsv` | `Figure_4/Figure_4_A` to `Figure_4_E`, `Figure_4_key` | B |
| 5 | `code/Figure_5.ipynb` | `qc_mutations.tsv`, `nonpublic/gene_by_endpoint.tsv`, `nonpublic/endpoints.tsv`, `nonpublic/distinct_mutations.tsv`, `pairwise_all_methods_gene.csv` | `Figure_5/Figure_5`, `Figure_5_A` to `Figure_5_D`, `Figure_5_key` | A |
| 6 | `code/Figure_6.py`, then `code/svg_for_illustrator.py` | nothing | `Figure_6/Figure_6` | B |
| S1 (Additional file 1) | `code/Figure_S1.ipynb` | `cache/Figure_S1_nulls.npz`, `pairwise_all_methods_gene.csv` | `Figure_S1/Figure_S1_A`, `Figure_S1_B` | B |
| S2 (Additional file 2) | `code/Figure_S2.ipynb` | `cache/Figure_S2_power_sweep.npz`, `per_experiment_summary_gene.csv` | `Figure_S2/Figure_S2`, `Figure_S2_AB`, `Figure_S2_C`, `Figure_S2_key_AB`, `Figure_S2_key_C` | A |

Each output is written as PNG at 300 dpi and as SVG with the text kept as editable text in Arial (only
the "−log10 q" axis title of Figure 4 A, which is math text, names DejaVu Sans). The panels of
Figure S1 are drawn at print size and are also written as PDF, with the PNG at 600 dpi. A file whose
name contains `_key` is a key, drawn on its own. Figures 1 and 3 are drawn whole, on one canvas each.
`Figure_5` holds panels A to D on one canvas, with the key inside panel A, each of B to D in a gray
box headed by its experiment's name, and the panel letters. `Figure_5_A` to `Figure_5_D` (A with its
own legend) hold the same panels as separate files, and `Figure_5_key` holds the key on its own.
`Figure_S2` holds panels A, B and C on one canvas, with the legend of A and B, the color bar of C and the
panel letters. `Figure_S2_AB` (panels A and B with their legend) and `Figure_S2_C` hold the same panels as
separate files, and `Figure_S2_key_AB` and `Figure_S2_key_C` hold the two keys on their own.

Figure 2 has no code in this folder. Its panel A is a schematic, and its panel B shows the two null
distributions of *rho* and *rpoB* in 42C_Tenaillon as normal curves, plotted outside this folder.

### Finished by hand in Adobe Illustrator

For Figures 1, 3 to 6, S1 and S2, the code draws every plotted element. The published figures were
assembled in Adobe Illustrator, which added:

- **Figures with panels:** the panel letters (Figures 1, 3, 5 and S2 draw their own), and the final size and layout.
- **Figure 2:** the whole figure was finished in Illustrator.
- **Figure 4:** the experiment names above panels B to E, the gray boxes and connector lines, and the place of the key.
- **Figure S1:** panel B placed as an inset at the top right of panel A, the legend moved to the upper left, and three text notes with a leader line on the most extreme possible overlaps.
- **Figure S2:** the labels "N = 70" and "N = 215" in panel C and the note on the settings of panel C.

## Rebuild the figures

1. Install conda (for example [Miniforge](https://github.com/conda-forge/miniforge)).
2. Create the two environments once. Their conda packages come from conda-forge only. Environment A
   also installs its plotting stack as pinned wheels from PyPI, because the PyPI matplotlib wheel
   carries the FreeType version its figures need.
   ```bash
   conda env create -f environments/environment_A.yml
   conda env create -f environments/environment_B.yml
   ```
3. Rebuild every figure from this folder (about one minute):
   ```bash
   bash run_all.sh
   ```
   Each notebook is executed in place, so its stored output shows the numbers of the run. To rebuild
   one notebook, run it the way `run_all.sh` does, with the environment named in the table above:
   ```bash
   JUPYTER_PREFER_ENV_PATH=1 PYTHONNOUSERSITE=1 conda run -n ale-paper-a --no-capture-output \
     python -m nbconvert --to notebook --execute --inplace code/Figure_1.ipynb
   ```
   For Figure 6, run the two `code/` commands of `run_all.sh` with `ale-paper-b`. The notebooks run
   from `code/`. To open them in Jupyter, register each environment's kernel once (for example
   `conda run -n ale-paper-a python -m ipykernel install --user --name ale-paper-a`) and choose that
   kernel.

Two environments are used so that the rebuilt PNG files match the article's files byte for byte: the
text in a PNG file is rendered by the FreeType library that matplotlib uses, and the two matplotlib
builds use different FreeType versions.

### Check the result

```bash
md5sum -c figures/MD5SUMS
```

compares every PNG file with the one made for the article. On Linux (x86-64) with these environments
they match byte for byte when neither Arial nor Helvetica is installed: matplotlib then renders the
text with its own DejaVu Sans font, as it did for the article's files. On a computer with Arial (for
example macOS), the PNG text is rendered in Arial and the files differ. SVG files change on every run
because matplotlib writes the date and random element ids into them, and the PDF files of Figure S1
carry their creation date.

## Data

`data/` holds copies of six output files of ale-cooccurrence-mutual-exclusivity-nf from the run used
for the article (commit `6835f2cc61def20df3619d05319a2744fbb7185b`, run on 2026-11-11 with
`nextflow run main.nf -params-file params/ecoli.yaml` in the pipeline's Docker image, on the
pipeline's input data together with the ALEdb deposits of STE_BOP, GLV, stALE and MS56_ALE_2022,
whose mutation data are not public). In these copies, `qc/ecoli/qc_mutations.tsv` has no rows of
these four experiments. For them, the files in `qc/ecoli/nonpublic/` hold only what the figures use.
Check all files with `md5sum -c data/MD5SUMS`.

| File | Content |
|---|---|
| `qc/ecoli/qc_mutations.tsv` | the mutation table after quality control, without the rows of the four experiments |
| `qc/ecoli/nonpublic/gene_by_endpoint.tsv` | the genes mutated in each endpoint of the four experiments (`exp`, `sample_endpoint`, `Gene_name_normalized`), the same table as `data/nonpublic_gene_by_endpoint.tsv` of the pipeline |
| `qc/ecoli/nonpublic/endpoints.tsv` | one row per endpoint of the four experiments, with its strain label (`strain_details`) and its experiment's condition label (`Condition_normalized`), with the values of the pipeline's mutation table |
| `qc/ecoli/nonpublic/mutation_types.tsv` | the number of mutations of each type in each of the four experiments (`exp`, `Mutation Type`, `n_mutations`) |
| `qc/ecoli/nonpublic/distinct_mutations.tsv` | the number of distinct mutations (distinct `Details` entries, as the notebooks count them for the other experiments) of each gene drawn for them in Figure 4 (panels D and E) and Figure 5 (panels B and D) (`exp`, `Gene_name_normalized`, `n_distinct_mutations`) |
| `qc/ecoli/qc_pipeline_report.tsv` | the numbers of records, experiments, endpoints and genes before and after each quality-control step |
| `qc/ecoli/checkpoints/02_select_species_summary.json` | counts recorded by the species selection step |
| `analysis/ecoli/all_experiments/pairwise_all_methods_gene.csv` | every candidate gene pair (two genes each mutated in at least two endpoints) of each analyzed experiment, with the results of Fisher's exact test and DISCOVER and the testability of each direction |
| `analysis/ecoli/all_experiments/per_experiment_summary_gene.csv` | one row per analyzed experiment |
| `analysis/ecoli/matrices/gene/42C_Tenaillon_.../matrix.csv` | the gene by endpoint matrix of the 42C_Tenaillon experiment, read by `code/Figure_S1_nulls.py` |

A run of the pipeline at the commit above on its public input data, which leaves out the deposits of
the four experiments, writes the same `qc/ecoli/qc_mutations.tsv` and the same 42C_Tenaillon matrix
as these copies. Its `pairwise_all_methods_gene.csv` and `per_experiment_summary_gene.csv` have the
same rows as these copies for every experiment other than the four. The commands under "Four
experiments that are not public" in the pipeline's README give the same rows of the four experiments
in these two tables, except for `n_input_rows` of the summary, which in their output counts one row
per gene and endpoint instead of one per mutation. On another computer, some numbers in these two
tables can differ in their later digits, as the pipeline's README notes. `qc_pipeline_report.tsv`
and `02_select_species_summary.json` also count the mutation records of the four experiments, so a
run without their deposits gives different numbers in these two files. The files in
`qc/ecoli/nonpublic/` are computed from the mutation records of the four experiments. Of them, only
`gene_by_endpoint.tsv` is also in the pipeline's input data, so the others cannot be rebuilt from
the public input data.

The mutation data come from ALEdb (Phaneuf et al. 2019, https://doi.org/10.1093/nar/gky983). Gene
names in `data/` were standardized with the STRING v12.0 alias file of E. coli K-12 MG1655
(https://string-db.org), which is under the Creative Commons Attribution 4.0 license (CC BY 4.0,
https://creativecommons.org/licenses/by/4.0/). Please also cite STRING (Szklarczyk et al. 2023,
https://doi.org/10.1093/nar/gkac1000) when you use them.

The code is written for the article's run: to use another run of the pipeline, put its six files in
`data/` (or set `DATA_DIR` in the first code cell of each notebook), rebuild both files in `cache/`,
and check the values listed under "Values set in the code", which belong to this run. The notebooks
of Figures 1, 3, 4 and 5 take the four experiments from `data/qc/ecoli/nonpublic/` in this folder
(`NONPUB_DIR`, in the same code cell as `DATA_DIR`), also when `DATA_DIR` points to another run, and
stop if that run's `qc_mutations.tsv` has rows of any of them.

## Precomputed values

- `cache/Figure_S1_nulls.npz` holds the two null distributions of the overlap of *glmS* and *rho* in
  42C_Tenaillon (Fisher's exact test and DISCOVER), their smallest attainable p-values, and the
  observed pattern of the two genes drawn in panel B. It is made by `code/Figure_S1_nulls.py` from the
  42C_Tenaillon matrix, which needs the DISCOVER package. DISCOVER is part of the pipeline's
  environment: build the pipeline's Docker image at the commit above (see `docker/README.md` in the
  pipeline repository), then run from this folder
  ```bash
  docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" -w /work \
    -e KMP_DUPLICATE_LIB_OK=TRUE ale-cooccurrence:dev python code/Figure_S1_nulls.py
  ```
  The pipeline's README also shows how to make the same environment with conda. DISCOVER's optimizer
  prints its own log while it fits the background model, and the log can end with
  `ABNORMAL_TERMINATION_IN_LNSRCH`, which the L-BFGS-B optimizer prints when its line search cannot
  improve the fit further. The script writes the cache only if each smallest attainable p-value
  matches the pair table, and `Figure_S1.ipynb` checks the cache against the pair table again.
- `cache/Figure_S2_power_sweep.npz` holds the exact power of the one-sided Fisher's exact test, at the
  single-pair threshold 0.05 and at the Bonferroni thresholds 0.05/m, over the number of lineages and
  the odds ratio. It is made by `code/Figure_S2_power_sweep.py` (which uses `code/power.py`) in
  environment B, in about four minutes:
  ```bash
  PYTHONNOUSERSITE=1 conda run -n ale-paper-b --no-capture-output python code/Figure_S2_power_sweep.py
  ```

Both scripts overwrite their file in `cache/`. Rebuilt this way on Linux (x86-64), both files are
identical to the ones used for the article, which `md5sum -c cache/MD5SUMS` checks.

## Values set in the code

| Value | Code | Meaning |
|---|---|---|
| `MIN_ENDPOINTS`, `D_ENDPOINT_MIN`, `E_ENDPOINT_MIN` = 2 | `Figure_1.ipynb` | `min_endpoints` of the pipeline's analysis configuration: experiments with fewer endpoints are not analyzed |
| `N_ENDPOINT_MIN` = 2 | `Figure_3.ipynb` | the same cut-off, for panel A |
| `TOP_N` = 10, `TOP_N_G` = 20 | `Figure_1.ipynb` | the genes in panel D and the condition categories in panel E |
| `THR_QQ` = −log10(0.05), `Q_THR` = 0.05 | `Figure_3.ipynb`, `Figure_4.ipynb` | where the dashed q = 0.05 lines are drawn. Which pairs are significant comes from the pair table (`fisher_sig_*`, `discover_sig_*`), set by `significance_threshold` in the pipeline's analysis configuration |
| `RENAME` | `Figure_4.ipynb`, `Figure_5.ipynb` | display names kpsE and kpsD for the E. coli B locus tags ECB_02815 and ECB_02816, following the mutation list of Tenaillon et al. 2012 (https://doi.org/10.1126/science.1212986) |
| `B_GENES` | `Figure_4.ipynb` | the rows of panel B, in the order of the two adaptive routes |
| `B_EXP`, `C_EXP`, `D_EXP`, `B_STRAIN_ORDER` | `Figure_5.ipynb` | the experiments of panels B to D, and the order of the strain blocks in panel B |
| `GENE_A`, `GENE_B`, `EXP_PREFIX` | `Figure_S1_nulls.py` | the gene pair and experiment of Figure S1 |
| `M_CO` = 5,482, `M_MUTEX` = 236 | `Figure_S2_power_sweep.py` | the numbers of 42C_Tenaillon pairs that Fisher's exact test can test for co-occurrence and for mutual exclusivity (rows with `fisher_testable_co` or `fisher_testable_mutex` true in the pair table), written into the script and held fixed while the number of lineages varies. The darker curves of panels A and B use the Bonferroni threshold `ALPHA` = 0.05/m |
| `F_REF` = 0.15 | `Figure_S2_power_sweep.py` | the fraction of lineages in which each gene of a pair is mutated |
| `N_TEN` = 111 | `Figure_S2.ipynb` | the number of endpoints of 42C_Tenaillon |
| odds ratios 10 and 1/10 | `Figure_S2.ipynb` | the effects of panels A and B |

## How to cite

If you use this code, please cite the article above, this code (`CITATION.cff` gives its citation
data), the pipeline ale-cooccurrence-mutual-exclusivity-nf, ALEdb (Phaneuf et al. 2019), and STRING
(Szklarczyk et al. 2023).

## License

The code is released under the MIT License (see `LICENSE`). The data in `data/` are derived from
ALEdb, and their gene names were standardized with STRING (see [Data](#data)). Please cite ALEdb
and STRING when you use them.
