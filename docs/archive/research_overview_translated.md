> English translation of the previous Chinese overview, retained for reference. The original is available at commit `7734111`. See the [current README](../../README.md).

# Where Do LLM Self-Improvement Gains Come From?

In 2025, a number of self-improvement methods reported gains without an external supervisor. I wanted to understand why training a model on its own outputs could make it better. How much of the improvement reflects new knowledge, and how much comes from the reward rules or the structure of the data?

I started by reproducing TTRL, inspecting responses before and after training, and running ablations. So far, I have not found clear evidence of new knowledge being acquired, but I have identified two concrete sources of improvement.

## How much does fixing the output format explain?

One problem stood out in the original model's responses: it often repeated itself, reached the length limit, or failed to put its answer inside `\boxed{...}`. TTRL relies on this format to extract answers for voting and reward calculation. A response that fails extraction gets no credit, even if the model could have answered the question.

This made me suspect that much of the gain came from teaching the model to finish its response and write its answer in the expected format.

I changed the reward to test this: any extractable boxed answer received a reward, regardless of whether its content was correct. The rest followed the TTRL experimental setup, and evaluation still checked answer correctness.

| Qwen2.5-Math-1.5B / MATH-TTT | Validation accuracy (`mean@16`) |
|---|---:|
| Before training | ~0.3200 |
| Full TTRL | 0.6625 |
| Format-only reward | 0.6285 |

The fraction of the full gain recovered was:

`(0.6285 - 0.3200) / (0.6625 - 0.3200) ≈ 90.1%`

In this experiment, rewarding format alone recovered about 90% of the improvement from full TTRL. This is the main evidence behind my conclusion that format correction accounts for a large part of the gain in this setting.

See [FINDINGS](../../docs/FINDINGS.md) for the results and [EXPERIMENTS](../../docs/EXPERIMENTS.md) for the commands.

## Why can voting get an answer right when greedy decoding gets it wrong?

Another pattern was that correct answers were often short integers, while wrong answers branched into different decimals spanning multiple tokens. Wrong answers could outnumber correct ones overall, yet each individual wrong answer received fewer votes.

Here is an example from my notes. For `68 / 34`, greedy decoding produced `1.946428`. Ten sampled responses were:

```text
1.946428
1.946...
2
1.946 (rounding
2
1.944947
1.852941
1
1.796428
2
```

Seven responses were wrong and three were right. But all three correct responses were `2`, so it won the vote. No new knowledge was needed for this selection: the correct answer was already in the model's output distribution and could now serve as a training pseudo-label.

I also observed this pattern on GSM8K: short integer answers collected votes, while different multi-token decimal errors split them. To study the process more closely, I constructed arithmetic problems with single-digit answers. I selected cases with longer greedy responses, at least one correct sampled answer, and several distinct sampled answers, then compared their behavior before and after training.

The code is in [research/vote_dispersion](../../research/vote_dispersion/). GSM8K multiple-choice preprocessing and the arithmetic experiment records are kept separately. The [research notes](../../research/vote_dispersion/RESEARCH_NOTES.md) describe how these experiments developed.

## Where I want to take this next

I originally planned to extend the experiments to more models, datasets, and self-improvement methods. As papers with similar conclusions began to appear, I became more interested in a different question: if biases in the reward system have such a large effect, can we deliberately design useful feedback?

This is the direction I hope to pursue during my PhD. My working view is that a self-training loop without useful feedback is unlikely to produce new knowledge reliably. Even without an external supervisor, the structure of the answers, voting rules, and format requirements still shape what the model learns. For self-improvement and recursive self-improvement (RSI), I want to understand where these feedback signals come from, when they help, and how to design them well.

## Repository contents

| Location | Contents |
|---|---|
| [research/vote_dispersion/](../../research/vote_dispersion/) | Original scripts, arithmetic records, and instructions for the vote-dispersion experiments |
| [research/vote_dispersion/gsm8k/](../../research/vote_dispersion/gsm8k/) | GSM8K multiple-choice preprocessing |
| [examples/ttrl/](../../examples/ttrl/) | TTRL training and checkpoint-loading scripts |
| [verl/trainer/ppo/ttrl_utils.py](../../verl/trainer/ppo/ttrl_utils.py) | TTRL pseudo-label voting |
| [analysis/](../../analysis/) and [results/](../../results/) | Format-reward analysis tools and result summaries |
| [docs/archive/](../../docs/archive/) | Earlier English and Chinese READMEs |

The archived scripts retain their original experimental logic. The [instructions](../../research/vote_dispersion/README.md) list dependencies, inputs, and execution order, along with the early inference and training scripts that have not yet been recovered.

The code builds on [veRL](https://github.com/volcengine/verl) and [TTRL](https://github.com/PRIME-RL/TTRL), with the original licenses and notices retained. See [PROVENANCE](../../docs/PROVENANCE.md) for the sources of the archived materials.
