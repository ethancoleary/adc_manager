import pandas as pd

in_dir = "/Users/ethanoleary/Documents/NHH/Projects/ADC/data/main/"
quartets = pd.read_csv(in_dir + "quartets_python_binned.csv")

# For each quartet_id, build a canonical representation based on
# the sorted list of (female, r2score) pairs.
def quartet_signature(group):
    # sort within quartet by r2score (and then gender) for stability
    g_sorted = group.sort_values(["r2score", "female"], ascending=[True, True])
    # build a tuple of pairs so that order is canonical
    return tuple(zip(g_sorted["female"].tolist(), g_sorted["r2score"].tolist()))

sig_df = (
    quartets
    .groupby("quartet_id", group_keys=False)
    .apply(quartet_signature)
    .reset_index(name="signature")
)

# Count how many times each signature occurs
sig_counts = (
    sig_df
    .value_counts("signature")
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)

top10 = sig_counts.head(20)

print("Top 10 most common quartets (by gender + r2score pattern):")
for i, row in top10.iterrows():
    print(f"Rank {i+1}: count={row['count']}, signature={row['signature']}")

top10_df = top10.copy()
top10_df["signature_str"] = top10_df["signature"].apply(
    lambda s: "; ".join([f"female={f}, r2={r:.3f}" for f, r in s])
)
print(top10_df[["count", "signature_str"]])