# Where Do LLM Self-Improvement Gains Come From?

Several self-improvement methods published in 2025 reported that models could improve without an external supervisor. I wanted to know what they were learning from their own outputs. Were they acquiring new knowledge, or getting better at things the reward rules already favored?

I studied this through TTRL, arithmetic experiments, and a lot of inspection of individual responses. I have not found clear evidence of new knowledge being acquired in these experiments. Two other explanations emerged: learning to produce an extractable answer, and learning from correct answers that voting could already recover.

## Learning to write the answer in the expected format

In the TTRL runs, the original model often repeated itself until it hit the length limit, or failed to put its answer inside `\boxed{...}`. The verifier needs that format to extract an answer. Failed extraction means no usable vote and no reward.

I suspected that much of the improvement came from fixing this behavior. To test it, I replaced the reward with a simple rule: give credit for any extractable boxed answer, even a wrong one. I kept the rest of the TTRL setup and still evaluated answer correctness.

| Qwen2.5-Math-1.5B / MATH-TTT | Validation accuracy (`mean@16`) |
|---|---:|
| Before training | ~0.3200 |
| Full TTRL | 0.6625 |
| Format-only reward | 0.6285 |

Format-only training recovered about **90% of the full gain**:

`(0.6285 - 0.3200) / (0.6625 - 0.3200) ≈ 90.1%`

For this model and setup, teaching it to produce a usable answer accounted for most of the measured improvement. [Results and sources](docs/FINDINGS.md) · [Run the experiments](docs/EXPERIMENTS.md)

## Correct answers collect votes; wrong answers split them

I also noticed that short integer answers could win a vote against many different, longer errors. This was especially apparent on GSM8K, where wrong outputs sometimes branched into multi-token decimals.

One arithmetic example from my notes was `68 / 34`. Greedy decoding returned `1.946428`. Ten samples gave:

```text
1.946428, 1.946..., 2, 1.946 (rounding, 2,
1.944947, 1.852941, 1, 1.796428, 2
```

Only three samples were correct, but all three were `2`. Each wrong answer appeared once. Voting picked the right answer from outputs the model could already generate.

### Training on cases where voting succeeds

To study this more closely, I constructed arithmetic problems whose correct answers were single characters, `0` through `9`. The model could still generate longer responses.

I started with 158,314 saved greedy predictions, selected the 1,613 longer responses, and sampled 20 answers for each question. Of those, 186 contained the correct answer and at least three distinct sampled answers. I kept the 80 with correct voting pseudo-labels and used them for training.

For example, on `212 / 212`, greedy decoding returned `100`:

| Sampled answer | Votes |
|---|---:|
| `1` (correct) | 9 |
| `10` | 2 |
| `101` | 5 |
| `100` | 4 |

The wrong responses outnumbered the correct ones 11 to 9, but split across three answers. So `1` won. Longer integer errors could produce the same effect as decimals.

Before training, greedy decoding got all 80 selected questions wrong. Training on the voting pseudo-labels changed that:

| On the selected 80 questions | Greedy accuracy |
|---|---:|
| Before training | 0/80 (0%) |
| After training | 68/80 (85%) |
| After one more epoch | 69/80 (86.25%) |

The model learned to reach, through greedy decoding, answers that voting had already found. These were the same questions used for training, selected using ground truth and pseudo-label correctness. The initial predictions are archived; the post-training counts come from my journal, since I have not recovered the full prediction files for those runs.

### Reducing the room for branching

An earlier experiment on 15,853 arithmetic questions tested the explanation from the other direction. I first strengthened the instruction to request exactly one single-digit non-negative integer. Then I compared only the first token of both greedy and sampled answers.

| Setting | Greedy wrong, vote right | Greedy right, vote wrong | Net voting advantage |
|---|---:|---:|---:|
| Original setup, 10 samples per question | 151 | 19 | +132 |
| Stronger single-digit instruction | 45 | 25 | +20 |
| First-token comparison for both methods | 21 | 28 | -7 |

Voting's net advantage fell from 132 questions to 20, then disappeared. That is what I would expect if multi-token branching explained much of its initial advantage.

I initially applied the first-token rule only to sampled answers. That was an unfair comparison: greedy decoding could start correctly and still be marked wrong for continuing. The final row applies the rule to both methods. These counts come from successive runs in my journal; their complete generation configurations have not yet been recovered.

The [research notes](research/vote_dispersion/RESEARCH_NOTES.md) contain the full counts and experiment history. The [code and saved records](research/vote_dispersion/) keep the arithmetic experiments separate from GSM8K preprocessing.

## What I want to work on next

I originally planned to repeat the analysis across more models and self-improvement methods. As papers with similar conclusions appeared, my interest shifted toward designing the feedback itself.

The format ablation and voting experiments both made me pay closer attention to what a system rewards. Without an external supervisor, answer structure, voting rules, and format requirements still influence what gets reinforced. I doubt that self-training can reliably discover new knowledge without some useful source of feedback.

During my PhD, I want to study how to build that feedback into self-improvement and recursive self-improvement (RSI) systems: what makes it reliable, where it fails, and how to improve it.

## Code and records

| Location | Contents |
|---|---|
| [research/vote_dispersion/](research/vote_dispersion/) | Arithmetic scripts, saved predictions, and instructions |
| [research/vote_dispersion/gsm8k/](research/vote_dispersion/gsm8k/) | GSM8K multiple-choice preprocessing |
| [examples/ttrl/](examples/ttrl/) | TTRL training and checkpoint-loading scripts |
| [verl/trainer/ppo/ttrl_utils.py](verl/trainer/ppo/ttrl_utils.py) | TTRL pseudo-label voting |
| [analysis/](analysis/) and [results/](results/) | Format-reward analysis and results |
| [docs/archive/](docs/archive/) | Earlier READMEs, translated into English |

The scripts retain their original experimental logic. Dependencies, inputs, execution order, and missing historical scripts are listed in the [instructions](research/vote_dispersion/README.md).

Built on [veRL](https://github.com/volcengine/verl) and [TTRL](https://github.com/PRIME-RL/TTRL), with their licenses and notices retained. See [PROVENANCE](docs/PROVENANCE.md) for the sources of the archived materials.
