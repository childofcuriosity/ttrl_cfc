# Vote-dispersion experiments and their sources

These notes follow the dates and sequence in the author's local research journal. The full journal remains local; the excerpts here cover the experiments represented by this archive.

## Starting with GSM8K: September 28, 2025

The initial plan was to use single-token outputs to study the relationship between greedy decoding and self-improvement. GSM8K was converted into multiple-choice questions, with the model restricted to A, B, C, or D. The notes then record poor performance from the small model under this restriction, followed by a move to controlled arithmetic problems with single-digit answers.

The recovered preprocessing script is `gsm8k/preprocess_gsm8k_mc.py`. The author's later account also describes vote dispersion between short integers and multi-token decimal errors on GSM8K. The arithmetic records in this directory are kept separate from that observation.

## Voting improved before training

The notes record higher pseudo-label accuracy as the number of samples increased, while greedy decoding stayed unchanged. Inspecting individual responses revealed branching decimal errors.

The original example was:

```text
Question: 68 / 34 =
Ground truth: 2
Greedy: 1.946428
Votes:
['1.946428', '1.946...', '2', '1.946 (rounding',
 '2', '1.944947', '1.852941', '1', '1.796428', '2']
Pseudo label: 2
```

The interpretation in the notes was that a wrong path could dominate at an early token and then branch into different final answers. Correct responses concentrated on the same string and won the vote.

Subsequent experiments examined single-digit prompts, first-token-only counting, numerical precision, top-p truncation, and sample count.

## Constructing a subset: October 23, 2025

The notes proposed three selection conditions: a longer greedy answer, at least one sampled ground-truth answer, and at least three distinct answers. The recovered code and records show the following sequence:

1. Select 1,613 longer answers from 158,314 saved greedy predictions.
2. Save multiple samples for these questions and count votes by answer string.
3. Select 186 cases containing GT and at least three distinct answers.
4. Retain the 80 cases with correct pseudo-labels.

The notes then describe saving those 80 cases as `arithmetic_dataset.csv` for training. The recovered files contain selection code and its inputs and outputs. The original inference and training entry points for this run have not been found, and no replacement implementation has been added.

### Quantitative results on the selected subset

The archived `selection/*pseudo_correct_only.csv` contains 80 questions: 74 division problems and 6 subtraction problems. Each has 20 sampled answers, an incorrect greedy prediction, and a correct pseudo-label. Thus, the initial greedy accuracy on this subset is 0/80, while pseudo-label accuracy is 80/80 by construction.

For `212 / 212`, the saved greedy prediction is `100`. The vote counts are `1: 9`, `10: 2`, `101: 5`, and `100: 4`. The correct answer wins despite incorrect responses accounting for 11 of the 20 samples.

The October 23 journal entry reports `Accuracy: 85.00% (68/80)` after training on these questions and notes the same accuracy for greedy and sampled evaluation. After another epoch, it records `Accuracy: 86.25% (69/80)`.

| Stage | Greedy accuracy | Evidence |
|---|---:|---|
| Before training | 0/80 (0%) | Recomputed from the archived CSV |
| After the initial training run | 68/80 (85%) | Journal entry |
| After one additional epoch | 69/80 (86.25%) | Journal entry |

The single-character constraint describes the correct answers, not a hard generation limit. The archived selection script uses character length greater than one as its historical proxy for multi-token output. These are selected training questions evaluated again after training, rather than a separate held-out set. Full post-training prediction files have not yet been recovered, so the two post-training figures are reported from the journal rather than presented as independently recomputed results.

## Moving to TTRL: October 24, 2025

A discussion highlighted the small overall gain in the early arithmetic experiments and the need to inspect real tasks where published methods reported larger improvements. The notes then turn to TTRL, followed by output analysis and the format-reward ablation.

This directory preserves the early vote-dispersion experiments. The existing TTRL code covers the later work. Both address where self-improvement gains come from, with their datasets and entry points kept separate.
