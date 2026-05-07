"""Pytest configuration and fixtures for le_slider_io tests."""

import json
import pytest
from pathlib import Path
from le_slider_io.schema import RatingRecordingSchema, CalibrationSchema


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
def sample_calib_schema():
    """Create a sample CalibrationSchema with typical data."""
    return CalibrationSchema(
        session_id="2026-04-24T13:15:36.008773+02:00",
        gain_calib=-12.5
    )


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for tests."""
    return str(tmp_path)


@pytest.fixture
def sample_json_file(tmp_path, sample_schema):
    """Create a temporary JSON file from sample RatingRecordingSchema."""
    json_path = tmp_path / "sample_recording.json"
    return sample_schema.to_json_file(json_path)


@pytest.fixture
def sample_calib_json_file(tmp_path, sample_calib_schema):
    """Create a temporary JSON file from sample CalibrationSchema."""
    json_path = tmp_path / "sample_calibration.json"
    return sample_calib_schema.to_json_file(json_path)


@pytest.fixture
def sample_json_dict(sample_schema):
    """Get the JSON-serializable dictionary from sample RatingRecordingSchema."""
    return sample_schema.to_json_dict()


@pytest.fixture
def sample_calib_json_dict(sample_calib_schema):
    """Get the JSON-serializable dictionary from sample CalibrationSchema."""
    return sample_calib_schema.to_json_dict()