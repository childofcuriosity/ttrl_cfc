# Sources of LLM self-improvement gains and evaluation bias

> English translation of the earlier Chinese README. The original is available in Git history at commit `7734111`. See the [current README](../../README.md) for the revised research overview.

This project uses TTRL to study whether unsupervised self-improvement gains reflect changes in reasoning or better compatibility between model outputs and the verifier's format requirements.

[Earlier English README](README.en.md) · [Experiments](../EXPERIMENTS.md) · [Findings](../FINDINGS.md)

## Main finding

In the Qwen2.5-Math-1.5B / MATH-TTT setting, format-only training reached **0.6285** validation accuracy. The same research record gives approximately **0.3200** before training and **0.6625** for full TTRL.

```text
(0.6285 - 0.3200) / (0.6625 - 0.3200) = 90.1%
```

![Format-only reward recovers about 90.1% of the observed full-TTRL gain.](../../results/main_results.svg)

In this setting, roughly 90% of the observed gain was associated with correcting format bias. At step 150, the log records a reward score of 0.972, a format score of 0.972, and answer accuracy of 0.628, separating format compliance from answer correctness.

The co-validation results provide a comparison:

| Model | Before training | Step 150 | Change |
|---|---:|---:|---:|
| Qwen2.5-Math-1.5B | 0.322688 | 0.669312 | +0.346624 |
| Qwen2.5-Math-1.5B-Instruct | 0.750469 | 0.758813 | +0.008344 |

The instruction-tuned model starts higher and changes much less. This comparison supports output/verifier compatibility as an important source of the measured gain.

## My work

- Reproduced and debugged TTRL with veRL and vLLM.
- Implemented before/after co-validation, temperature sweeps, response-length analysis, and voting analysis.
- Designed the format-reward ablation to measure format compliance separately from answer correctness.
- Ran experiments with three primary model configurations on MATH-500/MATH-TTT, AMC, and AIME, with an exploratory CommonsenseQA run.
- Organized the reward switch, result-extraction scripts, summaries, and scope documentation.

## Run the experiments

Standard reward:

```bash
bash examples/ttrl/run_reward_ablation.sh \
  accuracy examples/ttrl/Qwen2.5-Math/math.sh
```

Format-only reward:

```bash
bash examples/ttrl/run_reward_ablation.sh \
  format_only examples/ttrl/Qwen2.5-Math/math.sh
```

The mode is passed through `custom_reward_function.reward_kwargs.reward_mode`, which defaults to `accuracy`. Run these commands from the repository root.

See [Experiments](../EXPERIMENTS.md) for the environment, commands, and experiment coverage; [Findings](../FINDINGS.md), [Scope](../LIMITATIONS.md), and [Provenance](../PROVENANCE.md) describe the evidence and sources.
