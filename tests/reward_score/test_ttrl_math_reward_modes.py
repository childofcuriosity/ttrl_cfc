import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[2] / "verl/utils/reward_score/ttrl_math/reward_modes.py"
SPEC = importlib.util.spec_from_file_location("ttrl_reward_modes", MODULE_PATH)
reward_modes = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(reward_modes)


@pytest.mark.parametrize(
    ("is_correct", "has_format", "mode", "expected"),
    [
        (True, True, "accuracy", 1.0),
        (False, True, "accuracy", 0.0),
        (False, False, "accuracy", 0.0),
        (True, True, "format_only", 1.0),
        (False, True, "format_only", 1.0),
        (False, False, "format_only", 0.0),
    ],
)
def test_select_training_score(is_correct, has_format, mode, expected):
    result = reward_modes.select_training_score(
        is_correct=is_correct, has_format=has_format, reward_mode=mode
    )
    assert result == expected


def test_unknown_reward_mode_is_rejected():
    with pytest.raises(ValueError, match="Unknown reward_mode"):
        reward_modes.select_training_score(
            is_correct=True, has_format=True, reward_mode="unsupported"
        )
