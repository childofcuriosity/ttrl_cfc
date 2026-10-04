# Answer aggregation and vote dispersion

This directory contains the scripts and records for the second proposed source of improvement: when correct answers concentrate on a short integer while incorrect outputs branch into different decimals or longer strings, voting can recover a correct answer that greedy decoding misses.

The scripts were copied from the local research workspace. Their comments, console messages, and Chinese filenames have since been translated into English; parameters, selection rules, and experimental logic are unchanged. [SOURCES.json](SOURCES.json) records their origins and hashes. The experiment history was checked against the author's local research journal and is summarized in [RESEARCH_NOTES.md](RESEARCH_NOTES.md).

In the manifest, `source_sha256` and `bytes` describe the original local file. `archived_git_lf_sha256` identifies the copy before translation, and `git_lf_sha256` identifies the current file with LF line endings. Source paths are given as English renderings; the original paths remain in the manifest at commit `7734111`.

## Files

| File | Purpose |
|---|---|
| `arithmetic/main.py` | Enumerate arithmetic problems whose answers are integers from 0 to 9 |
| `selection/select_multi_token.py` | Select longer answers from saved greedy predictions |
| `selection/count_votes.py` | Count semicolon-separated sampled answers by string |
| `selection/filter_votes.py` | Select the two-answer control, cases containing GT and at least three distinct answers, and the correct-pseudo-label subset |
| `comparison/look.py` | Group before/after records by greedy, pseudo-label, and all-votes correctness |
| `comparison/mutil_greedy.py` | Select longer greedy answers and check whether their votes contain GT |
| `gsm8k/preprocess_gsm8k_mc.py` | Convert prepared GSM8K multiple-choice tables to CSV/Parquet with single-letter labels |

## Dependencies

Arithmetic generation, vote counting, filtering, and before/after comparison use pandas. GSM8K preprocessing also uses datasets and pyarrow.

```bash
python -m pip install -r research/vote_dispersion/requirements.txt
```

This list reflects the script imports and is not a version-locked reconstruction of the historical environment. See the existing environment records for GPU inference and training.

## Replay selection in a separate directory

Run these commands from the repository root. The temporary directory keeps generated files separate from the historical records.

```bash
repo="$PWD"
work="$(mktemp -d)"
cp research/vote_dispersion/selection/*.py "$work/"
cp research/vote_dispersion/selection/arithmetic_dataset_with_greedy.csv "$work/"
cp research/vote_dispersion/selection/arithmetic_dataset_with_greedy_multi_token_sampled.csv "$work/"
cd "$work"

python select_multi_token.py
python count_votes.py
python filter_votes.py

cd "$repo"
```

The saved processing stages are:

| File suffix | Rows | Meaning |
|---|---:|---|
| `with_greedy.csv` | 158,314 | Saved greedy predictions |
| `multi_token.csv` | 1,613 | Longer answers selected by the historical script |
| `multi_token_sampled.csv` | 1,613 | Saved samples for those questions |
| `with_counts.csv` | 1,613 | Votes counted by answer string |
| `pseudo_right_greedy_wrong_2votes.csv` | 29 | Correct pseudo-label, incorrect greedy answer, exactly two distinct answers |
| `contains_gt_more_than3_types.csv` | 186 | GT present and at least three distinct answers |
| `pseudo_correct_only.csv` | 80 | Correct pseudo-labels among those 186 cases |

These are controlled arithmetic experiments. The original greedy-inference and sampling launchers have not yet been located. The replay above reproduces postprocessing of saved predictions; it does not reconstruct inference or training.

## Compare before and after training

Copy the two scripts and two `*_model_full.csv` files from `comparison/` to a separate directory, then run:

```bash
python look.py
python mutil_greedy.py
```

`look.py` joins records by index and writes groups such as `B000_C100` to `results_64/`. The three bits represent greedy correctness, pseudo-label correctness, and whether all votes are correct. B denotes the base model and C the checkpoint.

`mutil_greedy.py` reads the checkpoint records by default and writes `long_greedy.csv` and `long_greedy_votes_match.csv`. Its historical filename is retained.

These files belong to a different arithmetic run from the 158,314 selection records and should not be concatenated with them.

## GSM8K preprocessing

The script reads CSVs with prepared answer options. Required fields are `question`, `options` (four choices), and `correct_answer`. Use input names ending in `_raw.csv`: the script removes `_raw` to form output names.

```bash
python research/vote_dispersion/gsm8k/preprocess_gsm8k_mc.py \
  --train_csv /path/to/train_with_options_raw.csv \
  --test_csv /path/to/test_with_options_raw.csv
```

The script uses seed 42, shuffles the options, and generates letter labels. Prepare the original questions and API-generated distractors separately. The GSM8K code here covers preprocessing; the arithmetic CSVs are not GSM8K results.

## Historical implementation details

- `select_multi_token.py` and `mutil_greedy.py` actually select strings longer than one character, without calling a tokenizer. The multi-token terminology comes from the original experiment.
- `count_votes.py` counts stripped answer strings without merging mathematically equivalent answers.
- The condition behind `more_than3_types` is `len(d) >= 3`.
- `filter_votes.py` uses GT to select cases for mechanism analysis. The 80-row subset is a deliberately selected set, not an unfiltered benchmark.
- Some scripts read and write files in the current directory at import time. Run them as standalone scripts.
- `arithmetic/main.py` enumerates both operands from 0 to 9,999. Generating the full dataset involves a large loop.
- English localization changes comments, documentation, messages, and filenames, not TTRL training, reward rules, or metric calculations.

## Verification

On 2026-10-04, the three selection scripts were replayed in a temporary directory and their CSV outputs matched the historical records cell for cell. Both comparison scripts ran successfully. Python syntax was checked. Full dataset generation, GSM8K preprocessing, and GPU experiments were not rerun.
