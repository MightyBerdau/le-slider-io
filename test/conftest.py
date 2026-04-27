"""Pytest configuration and fixtures for le_slider_io tests."""

import json
import pytest
from pathlib import Path
from le_slider_io.schema import RatingRecordingSchema


@pytest.fixture
def sample_schema():
    """Create a sample RatingRecordingSchema with typical data."""
    return RatingRecordingSchema(
        session_id="2026-04-24T13:15:36.008773+02:00",
        participant_id="VP001",
        stimulus_path="C:\\Audio\\S0N180_headrot_short.wav",
        stimulus_list="List2.txt",
        stimulus_start="2026-04-24T13:17:01.114975+02:00",
        stimulus_end="2026-04-24T13:17:07.659383+02:00",
        slider_config={
            "min": 0,
            "max": 10,
            "step": 0.1,
            "label": "Listening Effort"
        },
        ratings=[6.6, 6.6, 6.6, 6.7, 6.5, 6.4, 6.5],
        time_stamps=[0.0053, 0.0107, 0.0160, 0.0213, 0.0267, 0.0320, 0.0373]
    )


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for tests."""
    return str(tmp_path)


@pytest.fixture
def sample_json_file(tmp_path, sample_schema):
    """Create a temporary JSON file from sample schema."""
    json_path = tmp_path / "sample_recording.json"
    sample_schema.to_json_file(str(json_path))
    return str(json_path)


@pytest.fixture
def sample_json_dict(sample_schema):
    """Get the JSON-serializable dictionary from sample schema."""
    return sample_schema.to_json_dict()
