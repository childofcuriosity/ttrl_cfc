> Archived README. Current research overview: [README](../../README.md).

# 大模型自我提升的增益来源与评测偏差研究

本项目以 TTRL 为研究实例，考察无监督自我提升中的性能增益来自推理能力变化，还是模型输出与验证器格式之间的适配。

[English README](README.en.md) · [实验说明](../../docs/EXPERIMENTS.md) · [核心发现](../../docs/FINDINGS.md)

## 核心发现

在 Qwen2.5-Math-1.5B / MATH-TTT 设置中，仅使用格式奖励训练后，验证准确率达到 **0.6285**；同一研究记录中的训练前结果约为 **0.3200**，完整 TTRL 为 **0.6625**。

```text
(0.6285 - 0.3200) / (0.6625 - 0.3200) = 90.1%
```

![仅使用格式奖励恢复了完整 TTRL 约 90.1% 的观测增益。](../../results/main_results.svg)

在该设置中，约 90% 的观测增益与格式偏差纠正有关。训练日志在 step 150 同时记录了 0.972 的训练分数、0.972 的格式分数和 0.628 的答案准确率，清楚呈现了格式优化与答案正确率之间的区别。

作为对照，co-validation 结果显示：

| 模型 | 训练前 | Step 150 | 变化 |
|---|---:|---:|---:|
| Qwen2.5-Math-1.5B | 0.322688 | 0.669312 | +0.346624 |
| Qwen2.5-Math-1.5B-Instruct | 0.750469 | 0.758813 | +0.008344 |

已经具备较好格式适配能力的 Instruct 模型起点更高，训练后的变化明显更小。这一对照进一步表明，模型输出与外部验证器之间的适配是所测 TTRL 增益的重要来源。

## 我的工作

- 基于 veRL、vLLM 复现和调试 TTRL。
- 实现训练前后 co-validation、温度扫描、长度分析和投票行为分析。
- 设计格式奖励消融，将验证器格式适配与答案正确性分开测量。
- 在三个主要模型配置和 MATH-500/MATH-TTT、AMC、AIME 上开展实验，并探索 CommonsenseQA。
- 整理可复现的奖励开关、结果提取脚本、汇总表和研究边界。

## 快速运行

标准奖励：

```bash
bash examples/ttrl/run_reward_ablation.sh \
  accuracy examples/ttrl/Qwen2.5-Math/math.sh
```

格式奖励消融：

```bash
bash examples/ttrl/run_reward_ablation.sh \
  format_only examples/ttrl/Qwen2.5-Math/math.sh
```

奖励模式通过 `custom_reward_function.reward_kwargs.reward_mode` 传入，默认值为 `accuracy`。

完整环境、结果生成命令和实验覆盖范围见 [实验说明](../../docs/EXPERIMENTS.md)。已验证结果、后续测量和材料来源分别见 [核心发现](../../docs/FINDINGS.md)、[研究范围](../../docs/LIMITATIONS.md) 和 [材料来源](../../docs/PROVENANCE.md)。
