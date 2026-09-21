# Data and large artifacts

The experiment launchers expect processed datasets below `data/`, including:

- `MATH-TTT` / MATH-500
- `AMC-TTT`
- `AIME-TTT`
- `CommonsenseQA_Processed` for the exploratory cross-domain run

An archival project tarball is available at:

<https://huggingface.co/childofcuriosity/verl-backup-fdafsddfasfsda>

It contains the historical `verl/` workspace and processed mathematical
datasets. The archive is approximately 114 GB because it also includes large
artifacts. Extract it outside the Git repository and copy or link only the data
needed by the selected experiment.

Raw co-validation exports contain 500 prompts and up to 64 sampled responses per
prompt. Use `analysis/summarize_covalidate.py` to derive compact statistics.
