# Copyright 2025 YourName
# Licensed under the Apache License, Version 2.0
#
# Preprocess multiple-choice GSM8K dataset into parquet & CSV format (train/test).

import argparse
import os
import pandas as pd
import random
import datasets
import ast

# Fix the random seed for reproducibility.
RANDOM_SEED = 42
random.seed(RANDOM_SEED)


GSM8K_QUERY_TEMPLATE = (
    "{Question}\n"
    "A) {A}\nB) {B}\nC) {C}\nD) {D}\n"
)



def parse_options(opt_str):
    """Parse serialized options into a Python list."""
    if isinstance(opt_str, str):
        opt_str = opt_str.strip()
        if opt_str.startswith("["):
            try:
                return ast.literal_eval(opt_str)
            except Exception:
                return [s.strip() for s in opt_str.strip("[]").split(",")]
        else:
            return [s.strip() for s in opt_str.split(",")]
    return opt_str


def preprocess_gsm8k(csv_path: str):
    """Read a CSV into a Hugging Face Dataset."""
    df = pd.read_csv(csv_path)

    # Remove automatically generated Pandas index columns.
    drop_cols = [c for c in ["__index__", "__index_level_0__"] if c in df.columns]
    if drop_cols:
        print(f"🧹 Dropping unnecessary columns: {drop_cols}")
        df = df.drop(columns=drop_cols)

    df["options"] = df["options"].apply(parse_options)
    dataset = datasets.Dataset.from_pandas(df)
    return dataset


def make_map_fn(split_name):
    """Convert examples to the shared format."""
    def process_fn(example, idx):
        # import pdb; pdb.set_trace()
        opts = example["options"]
        if len(opts) != 4:
            raise ValueError(f"Options length != 4 for index {idx}")

        # Shuffle options using the fixed global seed.
        shuffled = list(zip("ABCD", opts))
        random.shuffle(shuffled)
        shuffled_labels, shuffled_opts = zip(*shuffled)
        opts = list(shuffled_opts)

        # Locate the correct answer after shuffling.
        correct_str = str(example["correct_answer"]).strip()
        gold_index = None
        for i, opt in enumerate(opts):
            if str(opt).strip() == correct_str:
                gold_index = i
                break

        if gold_index is None:
            raise ValueError(f"Correct answer {correct_str} not found in options: {opts}")

        gold_choice = "ABCD"[gold_index]

        # Build the prompt.
        query_prompt = GSM8K_QUERY_TEMPLATE.format(
            Question=example["question"],
            A=opts[0], B=opts[1], C=opts[2], D=opts[3]
        )

        # Keep the required fields.
        data = {
            "prompt": query_prompt,
            "ground_truth": gold_choice,
        }
        return data

    return process_fn

def process_and_save(csv_path: str, split: str, out_dir: str = None):
    """Write Parquet and CSV beside the input, removing _raw from the name."""
    print(f"\n📘 Processing split: {split}")
    dataset = preprocess_gsm8k(csv_path)
    dataset = dataset.map(function=make_map_fn(split), with_indices=True, num_proc=1, load_from_cache_file=False)

    # Get the input directory.
    input_dir = os.path.dirname(csv_path)

    # Remove "_raw" from the filename.
    base_name = os.path.basename(csv_path)
    base_name_no_raw = base_name.replace("_raw", "")
    file_stem = os.path.splitext(base_name_no_raw)[0]

    # Save beside the input file.
    parquet_path = os.path.join(input_dir, f"{file_stem}.parquet")
    csv_path_out = os.path.join(input_dir, f"{file_stem}.csv")

    # Write Parquet.
    dataset.to_parquet(parquet_path)

    # Write CSV.
    df = pd.DataFrame(dataset)
    df.to_csv(csv_path_out, index=False)

    print(f"✅ Saved {split} to:")
    print(f"   - {parquet_path}")
    print(f"   - {csv_path_out}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_csv", type=str, required=True, help="Path to train_with_options_raw.csv")
    parser.add_argument("--test_csv", type=str, required=True, help="Path to test_with_options_raw.csv")
    args = parser.parse_args()

    random.seed(RANDOM_SEED)

    process_and_save(args.train_csv, "train")
    process_and_save(args.test_csv, "test")

    print("\n🎉 All splits processed successfully!")
# python preprocess_gsm8k_mc.py  --train_csv ./train_with_options_raw.csv  --test_csv ./test_with_options_raw.csv
