# Result artifacts

- `main_results.csv` contains the three values used in the headline format-reward ablation.
- `format_only_curve.csv` is extracted directly from the preserved format-only training log by `analysis/extract_training_metrics.py`.
- `covalidate_summary.csv` is recomputed from four raw co-validation exports by `analysis/summarize_covalidate.py`.
- `main_results.svg` is the vector figure generated from `main_results.csv` by `analysis/plot_ablation.py`; the PNG copy is retained for quick previews.

The raw inputs remain outside Git because the co-validation exports occupy multiple gigabytes and contain complete model responses. See `docs/PROVENANCE.md` for their origin and `docs/LIMITATIONS.md` for the evidence scope.
