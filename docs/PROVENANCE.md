# Provenance

This repository is reconstructed from:

- the public `childofcuriosity/ttrl` code snapshot, `main@d6e6939`;
- the unmerged `update-work` environment export;
- local co-validation CSV exports and training logs dated 2025-11 to 2026-01;
- contemporaneous research notes describing the format-only intervention;
- the public Hugging Face archival tarball
  `childofcuriosity/verl-backup-fdafsddfasfsda`.

The original code base derives from veRL and retains its Apache-2.0 license and
notices. Project-specific contributions include TTRL experiment launchers,
majority-vote utilities, co-validation instrumentation, reward analysis and the
configurable format-only intervention.

Large model checkpoints, raw logs and multi-gigabyte CSV exports are kept out of
Git history. The committed summary tables can be regenerated with the scripts
in `analysis/` when the raw artifacts are available.
