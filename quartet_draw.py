import pandas as pd
import numpy as np

# path to your binned quartets file
path = "/Users/ethanoleary/Documents/NHH/Projects/ADC/Manager/quartets_python_binned.csv"

# load data
quartets = pd.read_csv(path)

# get unique quartet_ids, excluding 1200
ids = quartets["quartet_id"].unique()
ids = [i for i in ids if i != 1200]

# set RNG (optional: fixed seed for reproducibility)
rng = np.random.default_rng(17032008)

# sample 20 distinct quartet_ids
if len(ids) < 20:
    raise ValueError(f"Only {len(ids)} distinct quartet_ids available (excluding 1200).")

chosen_ids = rng.choice(ids, size=20, replace=False)

# subset to those quartets
sample_quartets = quartets[quartets["quartet_id"].isin(chosen_ids)].copy()

quartet_id_array = np.concatenate([chosen_ids, np.array([1200])])

rng = np.random.default_rng(17032008)  # choose any seed, or omit for non‑reproducible shuffle
rng.shuffle(quartet_id_array)        # shuffles in-place

print("Quartet ID array including 1200 at the end:")
print(quartet_id_array)