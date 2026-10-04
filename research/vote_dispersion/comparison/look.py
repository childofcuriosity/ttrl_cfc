import pandas as pd
import os

def split_csv_by_status(base_csv, checkpoint_csv, output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)

    # 读取
    base = pd.read_csv(base_csv)
    chk = pd.read_csv(checkpoint_csv)

    # 合并（按 index）
    merged = pd.merge(
        base, chk,
        on="index",
        suffixes=("_base", "_chk"),
        how="inner"
    )

    # 确保布尔字段为 True/False
    for col in [
        "greedy_correct_base", "pseudo_correct_base", "all_votes_correct_base",
        "greedy_correct_chk", "pseudo_correct_chk", "all_votes_correct_chk"
    ]:
        merged[col] = merged[col].astype(str).str.upper().isin(["TRUE", "1"])

    # 构造分组key
    def make_key(row):
        base_bits = ''.join(['1' if row[c] else '0' for c in [
            "greedy_correct_base", "pseudo_correct_base", "all_votes_correct_base"
        ]])
        chk_bits = ''.join(['1' if row[c] else '0' for c in [
            "greedy_correct_chk", "pseudo_correct_chk", "all_votes_correct_chk"
        ]])
        return f"B{base_bits}_C{chk_bits}"

    merged["status_group"] = merged.apply(make_key, axis=1)

    # 统计每组数量
    counts = merged["status_group"].value_counts().sort_index()
    print("✅ 分组情况：")
    print(counts)

    # 按组输出 CSV
    for group, df_group in merged.groupby("status_group"):
        out_path = os.path.join(output_dir, f"{group}.csv")
        df_group.to_csv(out_path, index=False)
        print(f"🟩 Saved: {out_path} ({len(df_group)} rows)")

    print(f"\n共输出 {len(counts)} 个分类文件到：{output_dir}")
    return counts, merged

# 运行示例
if __name__ == "__main__":
    counts, merged = split_csv_by_status(
        base_csv="base_model_full.csv",
        checkpoint_csv="checkpoint_model_full.csv",
        output_dir="results_64"
    )
