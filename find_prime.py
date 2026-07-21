import pandas as pd

path = "/Users/ethanoleary/Documents/NHH/Projects/ADC/Manager/quartets_python_binned.csv"
quartets = pd.read_csv(path)

target_top2 = [(1, 16), (0, 16)]
matches = []

for qid, grp in quartets.groupby("quartet_id"):
    # sort descending by r2score
    g_sorted = grp.sort_values("r2score", ascending=False)
    top2 = g_sorted.head(2)
    if len(top2) < 2:
        continue

    pairs = list(zip(top2["female"], top2["r2score"]))
    if pairs == target_top2:
        matches.append(qid)

print("Number of matching quartets:", len(matches))
print("Example matching quartet_ids:", matches[:20])

# If you want to inspect one in detail:
if matches:
    example_id = matches[0]
    print(quartets[quartets["quartet_id"] == example_id].sort_values("r2score", ascending=False))