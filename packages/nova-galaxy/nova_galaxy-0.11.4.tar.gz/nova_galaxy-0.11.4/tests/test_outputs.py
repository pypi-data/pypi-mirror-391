"""Tests for outputs."""

from nova.galaxy.dataset import Dataset, DatasetCollection
from nova.galaxy.outputs import Outputs


def test_output_dataset() -> None:
    outputs = Outputs()
    outputs.add_output(Dataset(path="test_files/test_text_file.txt", name="test_file"))
    assert outputs.get_dataset("test_file") is not None


def test_output_collection() -> None:
    outputs = Outputs()
    outputs.add_output(DatasetCollection(path="test_files/test_text_file.txt", name="test_file"))
    assert outputs.get_collection("test_file") is not None
