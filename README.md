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

See [FINDINGS](docs/FINDINGS.md) for the results and [EXPERIMENTS](docs/EXPERIMENTS.md) for the commands.

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

This pattern was especially clear on GSM8K: short integer answers collected votes, while different multi-token decimal errors split them. To make this source of improvement clear, I ran controlled experiments on arithmetic tasks whose correct outputs were single characters. I selected cases with longer greedy responses, at least one correct sampled answer, and several distinct sampled answers, then compared their behavior before and after training. These experiments made the role of vote dispersion easier to isolate and demonstrate.

### A controlled arithmetic experiment

I constructed arithmetic problems with answers from `0` to `9`. The correct answers were single characters, but generation was not forcibly limited to one character. From 158,314 saved greedy predictions, I selected 1,613 longer responses and sampled 20 answers per question. Of these, 186 had at least three distinct sampled answers and included the correct answer. I kept the 80 whose majority-vote pseudo-label was correct and used them for training.

One saved case was `212 / 212`. Greedy decoding returned `100`, while the samples split as follows:

| Sampled answer | Votes |
|---|---:|
| `1` (correct) | 9 |
| `10` | 2 |
| `101` | 5 |
| `100` | 4 |

The 11 wrong responses split across three answers, so the correct answer won with 9 votes. This also shows that the mechanism applies to longer integer errors, not just decimals.

All 80 selected questions were initially wrong under greedy decoding. After training on their pseudo-labels, the journal records:

| Evaluation on the selected 80 questions | Greedy accuracy | Source |
|---|---:|---|
| Before training | 0/80 (0%) | Archived predictions |
| After the initial training run | 68/80 (85%) | Research journal |
| After one additional epoch | 69/80 (86.25%) | Research journal |

This experiment shows how an answer already recoverable by voting can become available through greedy decoding after training. The 80 questions were selected using ground truth and pseudo-label correctness, then used for training and evaluation. The result demonstrates the mechanism on that subset; it is not a held-out generalization score. The post-training figures survive in the journal, while the corresponding full prediction files have not yet been recovered.

### What happens when the branching effect is reduced?

I also tested the explanation in the other direction. On an earlier set of 15,853 arithmetic questions, I first made the prompt explicitly request one single-digit non-negative integer. I then compared only the first token for both greedy decoding and sampled answers, removing differences caused by their continuations from the comparison.

| Setting | Greedy wrong, vote right | Greedy right, vote wrong | Net extra correct answers from voting |
|---|---:|---:|---:|
| Original setup, 10 samples per question | 151 | 19 | +132 |
| Stronger single-digit output instruction | 45 | 25 | +20 |
| First-token-only comparison for both methods | 21 | 28 | -7 |

The net advantage is the first count minus the second. As the comparison left less room for multi-token continuations to split votes, the voting advantage shrank from 132 questions to 20, then disappeared. This supports the interpretation that output branching was an important source of the original advantage.

An intermediate attempt counted only the first token of sampled answers while still evaluating the full greedy answer. That left an unequal comparison: greedy decoding could get the first token right and still fail by continuing. Applying the same first-token rule to both methods resolved this issue. These are sequential runs recorded in the research journal; their complete generation configurations have not yet been recovered.

The code is in [research/vote_dispersion](research/vote_dispersion/). GSM8K multiple-choice preprocessing and the arithmetic experiment records are kept separately. The [research notes](research/vote_dispersion/RESEARCH_NOTES.md) describe how these experiments developed and give the full comparison counts.

## Where I want to take this next

I originally planned to extend the experiments to more models, datasets, and self-improvement methods. As papers with similar conclusions began to appear, I became more interested in a different question: if biases in the reward system have such a large effect, can we deliberately design useful feedback?

This is the direction I hope to pursue during my PhD. My working view is that a self-training loop without useful feedback is unlikely to produce new knowledge reliably. Even without an external supervisor, the structure of the answers, voting rules, and format requirements still shape what the model learns. For self-improvement and recursive self-improvement (RSI), I want to understand where these feedback signals come from, when they help, and how to design them well.

## Repository contents

| Location | Contents |
|---|---|
| [research/vote_dispersion/](research/vote_dispersion/) | Original scripts, arithmetic records, and instructions for the vote-dispersion experiments |
| [research/vote_dispersion/gsm8k/](research/vote_dispersion/gsm8k/) | GSM8K multiple-choice preprocessing |
| [examples/ttrl/](examples/ttrl/) | TTRL training and checkpoint-loading scripts |
| [verl/trainer/ppo/ttrl_utils.py](verl/trainer/ppo/ttrl_utils.py) | TTRL pseudo-label voting |
| [analysis/](analysis/) and [results/](results/) | Format-reward analysis tools and result summaries |
| [docs/archive/](docs/archive/) | Earlier English and Chinese READMEs |

The archived scripts retain their original experimental logic. The [instructions](research/vote_dispersion/README.md) list dependencies, inputs, and execution order, along with the early inference and training scripts that have not yet been recovered.

The code builds on [veRL](https://github.com/volcengine/verl) and [TTRL](https://github.com/PRIME-RL/TTRL), with the original licenses and notices retained. See [PROVENANCE](docs/PROVENANCE.md) for the sources of the archived materials.
