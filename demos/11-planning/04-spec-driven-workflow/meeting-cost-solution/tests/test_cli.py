import subprocess
import sys
from pathlib import Path

import pytest

from meeting_cost.cli import main

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_valid_run_prints_total_and_exits_zero(capsys):
    assert main(["60", "100", "80", "60"]) == 0
    assert "240.00" in capsys.readouterr().out


def test_output_states_one_occurrence(capsys):
    main(["60", "100", "80", "60"])
    out = capsys.readouterr().out
    assert "Total (one occurrence): 240.00" in out
    assert "year" not in out
    assert "annual" not in out


def test_output_has_no_currency_symbol(capsys):
    main(["60", "100", "80", "60"])
    assert not any(symbol in capsys.readouterr().out for symbol in "$€£¥")


@pytest.mark.parametrize(
    ("argv", "field"),
    [
        (["0", "100"], "duration"),
        (["60"], "attendees"),
        (["60", "100", "-5"], "hourly rate"),
        (["60", "100", "abc"], "hourly rate"),
    ],
)
def test_invalid_input_exits_nonzero_naming_field(argv, field, capsys):
    assert main(argv) == 2
    assert field in capsys.readouterr().err


def test_hourly_rate_error_line_matches_contract(capsys):
    assert main(["60", "100", "-5"]) == 2
    assert capsys.readouterr().err == (
        'error: hourly rate for attendee 2: must be a finite number greater than or equal to zero, got "-5"\n'
    )


@pytest.mark.parametrize(
    "argv",
    [["0", "100"], ["60"], ["60", "100", "-5"], ["60", "100", "abc"]],
)
def test_invalid_input_prints_nothing_to_stdout(argv, capsys):
    main(argv)
    assert capsys.readouterr().out == ""


def test_module_runs_as_package():
    result = subprocess.run(
        [sys.executable, "-m", "meeting_cost", "30", "90"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "45.00" in result.stdout
