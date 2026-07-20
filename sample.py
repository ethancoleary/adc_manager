import pandas as pd
import numpy as np
from scipy.stats import ranksums  # Wilcoxon rank-sum (Mann-Whitney U) two-sided

# -----------------------------
# 0. Paths and constants
# -----------------------------
in_dir = "/Users/ethanoleary/Documents/NHH/Projects/ADC/Manager/"
out_dir = in_dir

FULL_QUARTETS_CSV = in_dir + "quartets_python_workers.csv"
FULL_QUARTET_STATS_CSV = in_dir + "quartet_stats_python.csv"
MAIN_DTA = in_dir + "main_cleaned.dta"

MAX_ITER = 1000  # safety cap; adjust as needed
TARGET_PVAL = 0.05
TARGET_GAP_P25 = 2.0
TARGET_MF_DIFF_MEAN_LOW = 1.16
TARGET_MF_DIFF_MEAN_HIGH = 1.74

# -----------------------------
# 1. Load full-universe files (once)
# -----------------------------
quartets_full = pd.read_csv(FULL_QUARTETS_CSV)
quartet_stats_full = pd.read_csv(FULL_QUARTET_STATS_CSV)

# Load main data for distribution tests
main_df = pd.read_stata(MAIN_DTA)
main_df = main_df.loc[main_df["treatment"].isin([1, 2])].copy()
main_df = main_df[["treatment", "female", "r2score"]].copy()
main_df = main_df.dropna(subset=["treatment", "female", "r2score"])

# -----------------------------
# 2. Helper: draw a new binned sample
# -----------------------------
def draw_binned(rng_seed):
    """
    Draw a new binned sample: 20 quartets per (self_female, self_r2).
    Returns (quartets_binned, quartet_stats_binned).
    """
    np.random.seed(rng_seed)

    kept_ids = (
        quartet_stats_full
        .groupby(["self_female", "self_r2"], group_keys=False)
        .apply(lambda g: g.sample(n=min(20, len(g)), replace=False))
        ["quartet_id"]
        .tolist()
    )
    kept_ids = set(kept_ids)

    qb = quartets_full[quartets_full["quartet_id"].isin(kept_ids)].copy()
    qsb = quartet_stats_full[quartet_stats_full["quartet_id"].isin(kept_ids)].copy()
    return qb, qsb

# -----------------------------
# 3. Helper: run the four ranksum tests
# -----------------------------
def run_ranksum_tests(quartets_binned):
    """
    Replicate the Stata ranksum tests:

    ranksum r2score if female == 0 & data_set < 2, by(data_set)
    ranksum r2score if female == 0 & data_set != 1, by(data_set)
    ranksum r2score if female == 1 & data_set < 2, by(data_set)
    ranksum r2score if female == 1 & data_set != 1, by(data_set)

    where:
      - data_set = 0 for quartets_binned
      - data_set = 1 for treatment==1 in main
      - data_set = 2 for treatment==2 in main
    """
    # Prepare quartet data
    q = quartets_binned[["female", "r2score"]].copy()
    q["data_set"] = 0

    # Prepare main data
    m = main_df.copy()
    m["data_set"] = m["treatment"]  # 1 or 2

    # Append
    combined = pd.concat([q, m], ignore_index=True)

    pvals = {}

    # Male: data_set < 2  (0 vs 1)
    male_01 = combined.loc[
        (combined["female"] == 0) & (combined["data_set"] < 2),
        ["r2score", "data_set"]
    ].dropna()
    x0 = male_01.loc[male_01["data_set"] == 0, "r2score"].values
    x1 = male_01.loc[male_01["data_set"] == 1, "r2score"].values
    _, p_male_01 = ranksums(x0, x1, alternative="two-sided")
    pvals["male_treat1"] = p_male_01

    # Male: data_set != 1  (0 vs 2)
    male_02 = combined.loc[
        (combined["female"] == 0) & (combined["data_set"] != 1),
        ["r2score", "data_set"]
    ].dropna()
    x0 = male_02.loc[male_02["data_set"] == 0, "r2score"].values
    x2 = male_02.loc[male_02["data_set"] == 2, "r2score"].values
    _, p_male_02 = ranksums(x0, x2, alternative="two-sided")
    pvals["male_treat2"] = p_male_02

    # Female: data_set < 2  (0 vs 1)
    fem_01 = combined.loc[
        (combined["female"] == 1) & (combined["data_set"] < 2),
        ["r2score", "data_set"]
    ].dropna()
    x0 = fem_01.loc[fem_01["data_set"] == 0, "r2score"].values
    x1 = fem_01.loc[fem_01["data_set"] == 1, "r2score"].values
    _, p_fem_01 = ranksums(x0, x1, alternative="two-sided")
    pvals["female_treat1"] = p_fem_01

    # Female: data_set != 1  (0 vs 2)
    fem_02 = combined.loc[
        (combined["female"] == 1) & (combined["data_set"] != 1),
        ["r2score", "data_set"]
    ].dropna()
    x0 = fem_02.loc[fem_02["data_set"] == 0, "r2score"].values
    x2 = fem_02.loc[fem_02["data_set"] == 2, "r2score"].values
    _, p_fem_02 = ranksums(x0, x2, alternative="two-sided")
    pvals["female_treat2"] = p_fem_02

    return pvals

# -----------------------------
# 4. Main loop: repeated sampling until all criteria met
# -----------------------------
seed_base = 12345  # starting seed; will increment each iteration

for it in range(1, MAX_ITER + 1):
    rng_seed = seed_base + it

    # 4a. Draw new binned sample
    quartets_binned, quartet_stats_binned = draw_binned(rng_seed)

    # 4b. Criterion 1: drop quartets with n_max_r2 >= 3
    # We enforce this by filtering quartet_stats_binned, then quartets_binned
    qsb_step1 = quartet_stats_binned[quartet_stats_binned["n_max_r2"] < 3].copy()
    kept_ids_step1 = set(qsb_step1["quartet_id"])
    qb_step1 = quartets_binned[quartets_binned["quartet_id"].isin(kept_ids_step1)].copy()

    # If no quartets survive, fail criterion 1 and continue
    if len(qsb_step1) == 0:
        print(f"Iter {it}: Criterion 1 FAILED (no quartets with n_max_r2 < 3).")
        print("  Criteria: [1]✗ [2]? [3]? [4]?")
        continue

    # From now on, work with the filtered set
    qb = qb_step1
    qsb = qsb_step1

    criterion1_ok = True  # by construction, if we got here

    # 4c. Criterion 2: ranksum tests (all 4 p-values > 0.05)
    pvals = run_ranksum_tests(qb)
    criterion2_ok = all(p > TARGET_PVAL for p in pvals.values())

    # 4d. Criterion 3: 25th percentile of gap_max_second == 2 among n_max_r2==1
    qsb_nmax1 = qsb[qsb["n_max_r2"] == 1].copy()
    if len(qsb_nmax1) == 0:
        gap_p25 = np.nan
        criterion3_ok = False
    else:
        gap_p25 = np.percentile(qsb_nmax1["gap_max_second"].dropna(), 25)
        criterion3_ok = np.isclose(gap_p25, TARGET_GAP_P25, atol=1e-8)

    # 4e. Criterion 4: mean of (avg_male_r2 - avg_female_r2) in [1.16, 1.74] among n_max_r2==1
    if len(qsb_nmax1) == 0:
        mf_diff_mean = np.nan
        criterion4_ok = False
    else:
        qsb_nmax1 = qsb_nmax1.dropna(subset=["avg_male_r2", "avg_female_r2"])
        if len(qsb_nmax1) == 0:
            mf_diff_mean = np.nan
            criterion4_ok = False
        else:
            mf_diff = qsb_nmax1["avg_male_r2"] - qsb_nmax1["avg_female_r2"]
            mf_diff_mean = mf_diff.mean()
            criterion4_ok = (
                TARGET_MF_DIFF_MEAN_LOW <= mf_diff_mean <= TARGET_MF_DIFF_MEAN_HIGH
            )

    # 4f. Print status
    def status(ok):
        return "✓" if ok else "✗"

    print(
        f"Iter {it}: "
        f"C1={status(criterion1_ok)} "
        f"C2={status(criterion2_ok)} "
        f"C3={status(criterion3_ok)} "
        f"C4={status(criterion4_ok)}"
    )
    if not criterion2_ok:
        print(
            f"  Ranksum p-values -> "
            f"male_treat1={pvals['male_treat1']:.4f}, "
            f"male_treat2={pvals['male_treat2']:.4f}, "
            f"female_treat1={pvals['female_treat1']:.4f}, "
            f"female_treat2={pvals['female_treat2']:.4f}"
        )
    if not criterion3_ok:
        print(f"  gap_max_second p25 (n_max_r2==1): {gap_p25:.4f} (target: {TARGET_GAP_P25})")
    if not criterion4_ok:
        print(
            f"  mean(avg_male_r2 - avg_female_r2) (n_max_r2==1): "
            f"{mf_diff_mean:.4f} (target: [{TARGET_MF_DIFF_MEAN_LOW}, {TARGET_MF_DIFF_MEAN_HIGH}])"
        )

    # 4g. Check if all criteria met
    if all([criterion1_ok, criterion2_ok, criterion3_ok, criterion4_ok]):
        print(f"\nAll criteria met at iteration {it} with seed {rng_seed}.")
        break
else:
    raise RuntimeError(
        f"Did not find a binned sample satisfying all criteria within {MAX_ITER} iterations."
    )

# -----------------------------
# 5. Save final binned files
# -----------------------------
qb.to_csv(out_dir + "quartets_python_binned.csv", index=False)
qb.to_stata(out_dir + "quartets_python_binned.dta", write_index=False)

qsb.to_csv(out_dir + "quartet_stats_python_binned.csv", index=False)
qsb.to_stata(out_dir + "quartet_stats_python_binned.dta", write_index=False)

print("Binned files saved:")
print(f"  - {out_dir}quartets_python_binned.*")
print(f"  - {out_dir}quartet_stats_python_binned.*")