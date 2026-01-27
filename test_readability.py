"""Test readability.py"""

import os
import sys
import subprocess
import pytest

base_param = [os.path.join(os.path.dirname(__file__), "readability")]
if sys.platform == "win32":
    base_param = ["python"] + base_param


def test_readability_empty():
    """Test readability.py"""
    param = base_param
    result = subprocess.run(
        param,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.stdout == "Usage: ./readability filename\n"


DATA_IN = [os.path.join(os.getcwd(), ".test", f"{i:0>2}.in") for i in range(1, 17)]

DATA_OUT = [
    "Before Grade 1",
    "Grade 2",
    "Grade 3",
    "Grade 5",
    "Grade 7",
    "Grade 7",
    "Grade 8",
    "Grade 9",
    "Grade 10",
    "Grade 16+",
    "Grade 11",
    "Grade 16+",
    "Grade 6",
    "Grade 8",
    "Grade 12",
]


@pytest.mark.parametrize(
    "input_data, expected_output",
    zip(DATA_IN, DATA_OUT),
)
def test_readability_single(input_data, expected_output):
    """Test readability.py"""
    param = base_param + [input_data]
    result = subprocess.run(
        param,
        input=input_data[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.stdout == f"{expected_output}\n"
