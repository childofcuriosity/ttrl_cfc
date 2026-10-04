import pandas as pd

def analyze_predictions(input_csv, output_filtered_csv=None):
    df = pd.read_csv(input_csv)

    # Strip whitespace.
    df["ground_truth"] = df["ground_truth"].astype(str).str.strip()
    df["predicted"] = df["predicted"].astype(str).str.strip()

    # Compute accuracy.
    df["correct"] = df["ground_truth"] == df["predicted"]
    accuracy = df["correct"].mean()
    print(f"✅ Accuracy: {accuracy:.2%} ({df['correct'].sum()}/{len(df)})")

    # Keep predictions longer than one character (the historical multi-token proxy).
    df_filtered = df[df["predicted"].str.len() > 1]

    if output_filtered_csv is None:
        output_filtered_csv = input_csv.replace(".csv", "_multi_token.csv")

    df_filtered.to_csv(output_filtered_csv, index=False)
    print(f"✅ Filtered CSV saved: {output_filtered_csv}")
    print(f"Filtered count: {len(df_filtered)}")

    return accuracy, output_filtered_csv


# Example invocation.
accuracy, filtered_path = analyze_predictions(
    input_csv="arithmetic_dataset_with_greedy.csv"
)
