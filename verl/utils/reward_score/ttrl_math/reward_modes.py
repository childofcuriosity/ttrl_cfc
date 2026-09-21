"""Training-score policies for the TTRL format-bias ablation."""

VALID_REWARD_MODES = frozenset({"accuracy", "format_only"})


def select_training_score(*, is_correct: bool, has_format: bool, reward_mode: str) -> float:
    """Return the scalar reward consumed by the veRL reward manager."""
    if reward_mode not in VALID_REWARD_MODES:
        choices = ", ".join(sorted(VALID_REWARD_MODES))
        raise ValueError(f"Unknown reward_mode={reward_mode!r}; expected one of: {choices}")
    if reward_mode == "format_only":
        return float(has_format)
    return float(is_correct)
