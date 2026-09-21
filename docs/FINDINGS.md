# Findings

## Main observation

On the recovered Qwen2.5-Math-1.5B / MATH-TTT run, format-only training reached
0.6285 validation accuracy, compared with approximately 0.3200 before training
and 0.6625 for the full TTRL run. The fraction of the full improvement recovered
by format-only training is:

```text
(0.6285 - 0.3200) / (0.6625 - 0.3200) = 0.9007
```

Thus, approximately 90% of the measured gain is associated with correcting
format compliance in this setting.

The training log supplies a second internal check. At step 150, the reward used
for training and the format score were both 0.972, while answer accuracy was
0.628. This separation is exactly what the `format_only` intervention predicts.

## Instruction-tuned control

The co-validation archives contain 500 prompts and 64 sampled answers per
prompt. Their aggregated vote-level accuracies are:

| Model | Pretrained | Step 150 | Change |
|---|---:|---:|---:|
| Qwen2.5-Math-1.5B | 0.322688 | 0.669312 | +0.346624 |
| Qwen2.5-Math-1.5B-Instruct | 0.750469 | 0.758813 | +0.008344 |

The model that already follows the expected answer format starts substantially
higher and shows a much smaller change. Together with the format-only
intervention, this control links the observed gain to adaptation between model
outputs and the verifier's extraction rule.

## Interpretation

TTRL optimizes against majority-vote pseudo-labels scored by an external answer
extractor. A model can improve the measured reward by producing more reliably
extractable `\\boxed{...}` answers. The observed score therefore contains both
reasoning performance and compatibility with the evaluator.

This distinction matters for test-time self-improvement: a higher benchmark
score can reflect improved task reasoning, improved interface compliance, or
both. The reward-mode intervention measures these components separately.
