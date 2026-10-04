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

## Moving to TTRL: October 24, 2025

A discussion highlighted the small overall gain in the early arithmetic experiments and the need to inspect real tasks where published methods reported larger improvements. The notes then turn to TTRL, followed by output analysis and the format-reward ablation.

This directory preserves the early vote-dispersion experiments. The existing TTRL code covers the later work. Both address where self-improvement gains come from, with their datasets and entry points kept separate.
