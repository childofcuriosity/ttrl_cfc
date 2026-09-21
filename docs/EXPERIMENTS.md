# Experiment matrix and reproduction

## Scope

The recovered study covers three primary model configurations:

- `Qwen2.5-Math-1.5B`
- `Qwen2.5-Math-1.5B-Instruct`
- `Llama-3.1-8B-Instruct`

The experiment scripts cover MATH-TTT/MATH-500, AMC and AIME. An exploratory
CommonsenseQA run with `Qwen2.5-1.5B` is preserved in the local research archive;
its launcher was not present in the recovered Git snapshot.

## Reward modes

| Field | Meaning | Used for training |
|---|---|---|
| `score` | Scalar selected by `reward_mode` | yes |
| `format_score` | Whether a boxed answer was extracted | logged |
| `acc` | Whether the extracted answer matches the label | logged |

`reward_mode=accuracy` reproduces the standard implementation.

`reward_mode=format_only` rewards extractable boxed output even when its answer
is incorrect.

## Commands

Standard TTRL:

```bash
bash examples/ttrl/run_reward_ablation.sh \
  accuracy \
  examples/ttrl/Qwen2.5-Math/math.sh
```

Format-only intervention:

```bash
bash examples/ttrl/run_reward_ablation.sh \
  format_only \
  examples/ttrl/Qwen2.5-Math/math.sh
```

Extra Hydra overrides can be appended to either command.

## Result extraction

```bash
python analysis/extract_training_metrics.py train.log \
  --output results/format_only_curve.csv

python analysis/summarize_covalidate.py \
  covalidate_preload.csv covalidate_loaded_step_150.csv \
  --output results/covalidate_recomputed.csv

python analysis/plot_ablation.py
```
