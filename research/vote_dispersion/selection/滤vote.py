import pandas as pd
import ast  # 用于解析 vote_counts 字典字符串

def split_filtered_csvs(input_csv):
    df = pd.read_csv(input_csv)

    # 解析 vote_counts 字典格式
    df["vote_counts"] = df["vote_counts"].apply(lambda x: ast.literal_eval(x))

    # ✅ Task 1
    cond1 = (
        (df["pseudo_correct"] == True) &
        (df["correct"] == False) &
        (df["vote_counts"].apply(lambda d: len(d) == 2))
    )
    df_task1 = df[cond1].copy()
    out1 = input_csv.replace(".csv", "_pseudo_right_greedy_wrong_2votes.csv")
    df_task1.to_csv(out1, index=False)
    print(f"✅ Task1 saved → {out1}, count = {len(df_task1)}")

    # ✅ Task 2
    def includes_gt_and_3types(row):
        d = row["vote_counts"]
        gt = str(row["ground_truth"]).strip()
        return (gt in d) and (len(d) >= 3)

    cond2 = df.apply(includes_gt_and_3types, axis=1)
    df_task2 = df[cond2].copy()
    out2 = input_csv.replace(".csv", "_contains_gt_more_than3_types.csv")
    df_task2.to_csv(out2, index=False)
    print(f"✅ Task2 saved → {out2}, count = {len(df_task2)}")

    return out1, out2
split_filtered_csvs("arithmetic_dataset_with_greedy_multi_token_sampled_with_counts.csv")

import pandas as pd

def filter_pseudo_correct(input_csv, output_csv=None):
    df = pd.read_csv(input_csv)

    # 只保留伪标签正确的
    df_filtered = df[df["pseudo_correct"] == True].copy()

    if output_csv is None:
        output_csv = input_csv.replace(".csv", "_pseudo_correct_only.csv")

    df_filtered.to_csv(output_csv, index=False)
    print(f"✅ Saved: {output_csv} (count: {len(df_filtered)})")

    return output_csv
filter_pseudo_correct(
    "arithmetic_dataset_with_greedy_multi_token_sampled_with_counts_contains_gt_more_than3_types.csv"
)
