import pandas as pd

# 1. Read the original file.
df = pd.read_csv("checkpoint_model_full.csv")

# 2. Keep greedy answers with more than one character.
df_long_greedy = df[df["greedy"].astype(str).str.len() > 1]

# 3. Save the filtered records.
df_long_greedy.to_csv("long_greedy.csv", index=False)

# 4. Votes are stored as a semicolon-separated string, e.g. "0; 0; 0; 0; 0".
# Check whether ground_truth occurs among the votes.
def has_ground_truth(row):
    # Split the votes and strip whitespace.
    votes = [v.strip() for v in str(row["votes"]).split(";")]
    return str(row["ground_truth"]).strip() in votes

# 5. Keep records whose votes contain ground_truth.
df_votes_match = df_long_greedy[df_long_greedy.apply(has_ground_truth, axis=1)]

# 6. Save the second subset.
df_votes_match.to_csv("long_greedy_votes_match.csv", index=False)

print(f"Greedy answers longer than one character: {len(df_long_greedy)}; votes containing ground_truth: {len(df_votes_match)}.")
