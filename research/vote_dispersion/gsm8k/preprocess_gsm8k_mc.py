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

# 固定随机种子，保证复现性
RANDOM_SEED = 42
random.seed(RANDOM_SEED)


GSM8K_QUERY_TEMPLATE = (
    "{Question}\n"
    "A) {A}\nB) {B}\nC) {C}\nD) {D}\n"
)



def parse_options(opt_str):
    """确保 options 从字符串解析为 Python 列表"""
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
    """读取 CSV 并转换为 HuggingFace Dataset"""
    df = pd.read_csv(csv_path)

    # ✅ 删除 Pandas 自动加的 index 列
    drop_cols = [c for c in ["__index__", "__index_level_0__"] if c in df.columns]
    if drop_cols:
        print(f"🧹 Dropping unnecessary columns: {drop_cols}")
        df = df.drop(columns=drop_cols)

    df["options"] = df["options"].apply(parse_options)
    dataset = datasets.Dataset.from_pandas(df)
    return dataset


def make_map_fn(split_name):
    """转换为统一格式"""
    def process_fn(example, idx):
        # import pdb; pdb.set_trace()
        opts = example["options"]
        if len(opts) != 4:
            raise ValueError(f"Options length != 4 for index {idx}")

        # ✅ 随机打乱选项（全局种子已固定）
        shuffled = list(zip("ABCD", opts))
        random.shuffle(shuffled)
        shuffled_labels, shuffled_opts = zip(*shuffled)
        opts = list(shuffled_opts)

        # ✅ 找到正确答案的新索引
        correct_str = str(example["correct_answer"]).strip()
        gold_index = None
        for i, opt in enumerate(opts):
            if str(opt).strip() == correct_str:
                gold_index = i
                break

        if gold_index is None:
            raise ValueError(f"Correct answer {correct_str} not found in options: {opts}")

        gold_choice = "ABCD"[gold_index]

        # ✅ 构造 prompt
        query_prompt = GSM8K_QUERY_TEMPLATE.format(
            Question=example["question"],
            A=opts[0], B=opts[1], C=opts[2], D=opts[3]
        )

        # ✅ 精简后的数据结构
        data = {
            "prompt": query_prompt,
            "ground_truth": gold_choice,
        }
        return data

    return process_fn

def process_and_save(csv_path: str, split: str, out_dir: str = None):
    """加载、转换并保存为 parquet & csv（同目录输出，去掉 _raw）"""
    print(f"\n📘 Processing split: {split}")
    dataset = preprocess_gsm8k(csv_path)
    dataset = dataset.map(function=make_map_fn(split), with_indices=True, num_proc=1, load_from_cache_file=False)

    # 获取输入目录
    input_dir = os.path.dirname(csv_path)

    # 去掉文件名中的 "_raw"
    base_name = os.path.basename(csv_path)
    base_name_no_raw = base_name.replace("_raw", "")
    file_stem = os.path.splitext(base_name_no_raw)[0]

    # 输出路径：与输入同目录
    parquet_path = os.path.join(input_dir, f"{file_stem}.parquet")
    csv_path_out = os.path.join(input_dir, f"{file_stem}.csv")

    # 保存 parquet
    dataset.to_parquet(parquet_path)

    # 保存 csv
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