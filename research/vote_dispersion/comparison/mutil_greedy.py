import pandas as pd

# 1. 读取原始文件
df = pd.read_csv("checkpoint_model_full.csv")

# 2. 过滤出 greedy 的答案长度大于 1 的
df_long_greedy = df[df["greedy"].astype(str).str.len() > 1]

# 3. 保存这个结果
df_long_greedy.to_csv("long_greedy.csv", index=False)

# 4. votes 列的内容是用分号分隔的字符串，例如 "0; 0; 0; 0; 0"
# 我们希望判断 ground_truth 是否出现在 votes 中
def has_ground_truth(row):
    # 去除空格并拆分
    votes = [v.strip() for v in str(row["votes"]).split(";")]
    return str(row["ground_truth"]).strip() in votes

# 5. 从上一个筛选结果中过滤出 votes 含有 ground_truth 的
df_votes_match = df_long_greedy[df_long_greedy.apply(has_ground_truth, axis=1)]

# 6. 保存第二个结果
df_votes_match.to_csv("long_greedy_votes_match.csv", index=False)

print(f"greedy长度>1的共有 {len(df_long_greedy)} 条，且votes中含有ground_truth的共有 {len(df_votes_match)} 条。")
