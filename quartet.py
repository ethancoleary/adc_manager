import pandas as pd
import numpy as np

# -----------------------------
# 1. Load data (now including r3score)
# -----------------------------
df = pd.read_stata("/Users/ethanoleary/Documents/NHH/Projects/ADC/data/main/main_cleaned.dta")

# Keep treatment 2 only
df = df.loc[df["treatment"] == 2].copy()

# Treat each participantlabel as a worker_id
df = df[["participantlabel", "female", "r2score", "r3score"]].copy()
df = df.dropna(subset=["participantlabel", "female", "r2score"])

# If you also want to require non-missing r3score, uncomment:
# df = df.dropna(subset=["r3score"])

# -----------------------------
# 2. Gender-specific pools (sampling with replacement)
# -----------------------------
pool_f = df.loc[df["female"] == 1].copy()
pool_m = df.loc[df["female"] == 0].copy()

pool_f["w"] = 1.0
pool_m["w"] = 1.0

if pool_f["w"].sum() == 0 or pool_m["w"].sum() == 0:
    raise ValueError("Sampling weights sum to zero in one gender pool.")

# -----------------------------
# 3. For each worker, draw 20 quartets including that worker
# -----------------------------
rng_seed = 987654
results = []

workers = df[["participantlabel", "female", "r2score"]].drop_duplicates().reset_index(drop=True)

for idx, w in workers.iterrows():
    worker_id = w["participantlabel"]
    worker_female = int(w["female"])
    worker_r2 = w["r2score"]

    for rep in range(1, 21):
        # Self row
        self_row = {
            "worker_id": worker_id,
            "rep": rep,
            "role": "self",
            "quartet_pos": 1,
            "participantlabel": worker_id,
            "female": worker_female,
            "r2score": worker_r2,
        }
        results.append(self_row)

        # Draw the other 3
        if worker_female == 1:
            # worker female → 1 more F + 2 M
            draw_f = pool_f.sample(
                n=1, replace=True, weights="w",
                random_state=rng_seed + idx * 1000 + rep
            )
            draw_m = pool_m.sample(
                n=2, replace=True, weights="w",
                random_state=rng_seed + idx * 1000 + rep + 1
            )
            draws = pd.concat([draw_f, draw_m], ignore_index=True)
        else:
            # worker male → 2 F + 1 more M
            draw_f = pool_f.sample(
                n=2, replace=True, weights="w",
                random_state=rng_seed + idx * 1000 + rep
            )
            draw_m = pool_m.sample(
                n=1, replace=True, weights="w",
                random_state=rng_seed + idx * 1000 + rep + 1
            )
            draws = pd.concat([draw_f, draw_m], ignore_index=True)

        draws = draws.reset_index(drop=True)
        draws["worker_id"] = worker_id
        draws["rep"] = rep
        draws["role"] = "other"
        draws["quartet_pos"] = [2, 3, 4]

        results.extend(draws[[
            "worker_id", "rep", "role", "quartet_pos",
            "participantlabel", "female", "r2score"
        ]].to_dict("records"))

# -----------------------------
# 4. Quartet-level dataset (long format)
# -----------------------------
quartets = pd.DataFrame(results).sort_values(["worker_id", "rep", "quartet_pos"])

quartets["quartet_id"] = pd.factorize(
    pd.Series(list(zip(quartets["worker_id"], quartets["rep"])))
)[0] + 1

# Merge in r3score by participantlabel
# (assumes r3score is constant within participantlabel in treatment 2)
r3_lookup = df[["participantlabel", "r3score"]].drop_duplicates()
quartets = quartets.merge(r3_lookup, on="participantlabel", how="left")

# -----------------------------
# 5. Quartet-level stats (including pattern)
# -----------------------------
def quartet_full_stats(group):
    # sort by r2score descending
    g_sorted = group.sort_values("r2score", ascending=False)
    scores = g_sorted["r2score"].values

    max_r2 = scores[0]
    second_r2 = scores[1]
    min_r2 = scores[-1]

    gap_max_second = max_r2 - second_r2
    gap_max_min = max_r2 - min_r2

    # number of observations at the maximum r2score
    n_max = (group["r2score"] == max_r2).sum()

    # averages by gender (r2score)
    males = group.loc[group["female"] == 0, "r2score"]
    females = group.loc[group["female"] == 1, "r2score"]

    avg_male_r2 = males.mean() if len(males) > 0 else np.nan
    avg_female_r2 = females.mean() if len(females) > 0 else np.nan

    # pattern M/F by rank
    pattern = "".join(g_sorted["female"].map({1: "F", 0: "M"}).tolist())

    # self observation (role == "self")
    self_row = group.loc[group["role"] == "self"].iloc[0]
    self_female = int(self_row["female"])
    self_r2 = self_row["r2score"]

    return pd.Series({
        "pattern": pattern,
        "max_r2": max_r2,
        "gap_max_second": gap_max_second,
        "gap_max_min": gap_max_min,
        "avg_male_r2": avg_male_r2,
        "avg_female_r2": avg_female_r2,
        "self_female": self_female,
        "self_r2": self_r2,
        "n_max_r2": n_max,
    })

quartet_stats_df = quartets.groupby("quartet_id").apply(quartet_full_stats).reset_index()

# -----------------------------
# 6. Extract rank1–rank4 gender from pattern
# -----------------------------
quartet_stats_df["rank1_gender"] = quartet_stats_df["pattern"].str[0]
quartet_stats_df["rank2_gender"] = quartet_stats_df["pattern"].str[1]
quartet_stats_df["rank3_gender"] = quartet_stats_df["pattern"].str[2]
quartet_stats_df["rank4_gender"] = quartet_stats_df["pattern"].str[3]

def gini_from_array(x):
    """Compute Gini coefficient for a 1D array-like of non-negative values."""
    x = np.asarray(x, dtype=float)
    n = x.size
    if n == 0:
        return np.nan
    mean_x = x.mean()
    if mean_x == 0:
        return 0.0
    xs = np.sort(x)
    i = np.arange(1, n + 1)
    S = np.sum((2 * i - n - 1) * xs)
    return S / (n**2 * mean_x)

gini_by_quartet = (
    quartets.groupby("quartet_id")["r2score"]
    .apply(gini_from_array)
    .rename("gini_r2")
    .reset_index()
)

# Merge into quartet_stats_df
quartet_stats_df = quartet_stats_df.merge(gini_by_quartet, on="quartet_id", how="left")

# -----------------------------
# 7. Save full-universe files
# -----------------------------
out_dir = "/Users/ethanoleary/Documents/NHH/Projects/ADC/Manager/"

quartets.to_csv(out_dir + "quartets_python_workers.csv", index=False)
quartets.to_stata(out_dir + "quartets_python_workers.dta", write_index=False)

quartet_stats_df.to_csv(out_dir + "quartet_stats_python.csv", index=False)
quartet_stats_df.to_stata(out_dir + "quartet_stats_python.dta", write_index=False)