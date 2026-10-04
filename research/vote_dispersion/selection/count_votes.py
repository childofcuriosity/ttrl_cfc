import pandas as pd

def add_vote_counts_column(input_csv, output_csv=None):
    df = pd.read_csv(input_csv)

    vote_counts = []

    for votes_str in df["votes"]:
        # votes: "1; 10; 100; ..."
        votes = [v.strip() for v in votes_str.split(";") if v.strip() != ""]
        freq = {}
        for v in votes:
            freq[v] = freq.get(v, 0) + 1
        vote_counts.append(freq)

    df["vote_counts"] = vote_counts  # Store a dictionary in the new column.

    if output_csv is None:
        output_csv = input_csv.replace(".csv", "_with_counts.csv")

    df.to_csv(output_csv, index=False)
    print(f"✅ Saved with vote_counts → {output_csv}")
    return output_csv
add_vote_counts_column("arithmetic_dataset_with_greedy_multi_token_sampled.csv")
