# 多数投票中的答案聚合与分支分票

本目录归档研究第二条增益路径的原始源码：当正确答案集中于短整数，而错误输出分叉成不同小数或长字符串时，多数投票如何选出贪心未选中的正确答案。

脚本直接复制自本地研究目录，保持原文件名、参数、筛选规则和实验逻辑。来源与 SHA-256 校验和见 [SOURCES.json](SOURCES.json)。研究过程按一手日志《做法.docx》核对，摘录见 [RESEARCH_NOTES.md](RESEARCH_NOTES.md)。

清单中的 `source_sha256` 对应原始文件字节，`git_lf_sha256` 对应 Git 统一为 LF 换行后的内容，`bytes` 为原始文件大小。

2026-10-04 整理验证：在独立临时目录运行三个 selection 脚本，生成 CSV 与历史记录逐单元格一致；两个 comparison 脚本运行通过。所有归档 Python 文件通过语法检查。未重跑全集生成、GSM8K 预处理或 GPU 实验。

## 文件与作用

| 目录 / 文件 | 作用 |
|---|---|
| `arithmetic/main.py` | 枚举四则运算，保留答案为 0–9 的题目 |
| `selection/选多token.py` | 从贪心预测记录筛选较长输出 |
| `selection/给vote计数.py` | 对分号分隔的采样答案按字符串计票 |
| `selection/滤vote.py` | 筛选两答案对照、含 GT 且至少三个答案的样本，以及伪标签正确子集 |
| `comparison/look.py` | 按训练前后的贪心、伪标签、全部票正确性分组 |
| `comparison/mutil_greedy.py` | 筛选较长贪心输出，并检查采样是否包含 GT |
| `gsm8k/preprocess_gsm8k_mc.py` | 将已有 GSM8K 选择题原始表转为单字母答案的 CSV / Parquet |

## 依赖

算术生成、计票、筛选和前后对比使用 pandas；GSM8K 预处理额外使用 datasets 与 pyarrow。

```bash
python -m pip install -r research/vote_dispersion/requirements.txt
```

此依赖列表按源码导入整理，未锁定为当时训练环境。GPU 推理和训练环境仍见仓库已有环境记录。

## 在独立工作目录重放筛选

以下命令在仓库根目录执行，使用临时目录，避免覆盖归档的历史结果：

```bash
repo="$PWD"
work="$(mktemp -d)"
cp research/vote_dispersion/selection/*.py "$work/"
cp research/vote_dispersion/selection/arithmetic_dataset_with_greedy.csv "$work/"
cp research/vote_dispersion/selection/arithmetic_dataset_with_greedy_multi_token_sampled.csv "$work/"
cd "$work"

python 选多token.py
python 给vote计数.py
python 滤vote.py

cd "$repo"
```

保存数据对应的处理链为：

| 文件后缀 | 行数 | 含义 |
|---|---:|---|
| `with_greedy.csv` | 158,314 | 已保存的贪心预测 |
| `multi_token.csv` | 1,613 | 原脚本筛选出的较长回答 |
| `multi_token_sampled.csv` | 1,613 | 对这些回答保存的采样记录 |
| `with_counts.csv` | 1,613 | 按答案字符串计票 |
| `pseudo_right_greedy_wrong_2votes.csv` | 29 | 伪标签对、贪心错，且恰好两个不同答案 |
| `contains_gt_more_than3_types.csv` | 186 | 包含 GT，且至少三个不同答案 |
| `pseudo_correct_only.csv` | 80 | 上述 186 条中伪标签正确的子集 |

这些数据是可控算术实验记录。贪心预测和多次采样的原始执行脚本尚未在此次定位的本地文件中找到，因此这里可重放的是保存结果的后处理链，未重建推理或训练算法。

## 训练前后对比

在独立目录复制 `comparison/` 中的两个脚本与两个 `*_model_full.csv`，运行：

```bash
python look.py
python mutil_greedy.py
```

`look.py` 按 index 合并训练前后记录，输出 `results_64/`，组名如 `B000_C100`。三位依次表示贪心正确、伪标签正确、全部票正确；B 为原模型，C 为 checkpoint。`mutil_greedy.py` 默认读取 checkpoint，输出 `long_greedy.csv` 和 `long_greedy_votes_match.csv`。

这些是另一组历史算术实验文件，不应与 selection 的 158,314 条记录直接拼接。

## GSM8K 预处理

原脚本读取已经构造好选项的 CSV，所需字段为 `question`、`options`（四个选项）、`correct_answer`。输入文件须以 `_raw.csv` 结尾，脚本通过去掉 `_raw` 构造输出名：

```bash
python research/vote_dispersion/gsm8k/preprocess_gsm8k_mc.py \
  --train_csv /path/to/train_with_options_raw.csv \
  --test_csv /path/to/test_with_options_raw.csv
```

脚本固定随机种子为 42，打乱选项顺序后生成字母标签。原始问题数据及 API 生成干扰选项的环节需另行准备；本目录归档的 GSM8K 源码是数据预处理，算术 CSV 不标作 GSM8K 结果。

## 原始实现约定

- `选多token.py` 和 `mutil_greedy.py` 实际使用字符串字符数大于 1 筛选，未调用 tokenizer；保留“多 token”的历史文件名。
- `给vote计数.py` 按去除首尾空白后的答案字符串计票，没有数学等价类合并。
- `more_than3_types` 的实际条件为 `len(d) >= 3`。
- `滤vote.py` 使用 GT 选择研究样本。这是机制分析用的条件筛选，80 条子集不能当作未经筛选的基准。
- 部分脚本在导入时就读写当前目录文件，应作为独立脚本运行。
- `arithmetic/main.py` 的原始范围为两个操作数各 0–9999，循环规模较大；本次未执行数据全集生成。
- 此次整理未修改 TTRL 训练逻辑、格式奖励实现或既有指标。
