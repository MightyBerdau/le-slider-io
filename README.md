# le slider io

A lightweight Python library for managing and persisting audio rating recordings from the [le slider project](https://github.com/MightyBerdau/le-slider.git). Provides schema definition and utilities for serializing slider-based rating data to JSON format.

## Table of Contents

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Basic Usage: Create and Save a Recording](#basic-usage-create-and-save-a-recording)
  - [Load a Recording](#load-a-recording)
  - [Calculate Timestamps Automatically](#calculate-timestamps-automatically)
  - [Batch Load Recordings](#batch-load-recordings)
  - [Manual JSON Serialization](#manual-json-serialization)
  - [JSON Output Format](#json-output-format)
- [API Reference](#api-reference)
  - [RatingRecordingSchema](#ratingrecordingschema)
  - [Recording Utilities](#recording-utilities)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Citation](#citation)

___

# Installation

## Requirements

- Python >= 3.11.3
- No external dependencies for core functionality
- Development: pytest, pytest-cov (optional)

```bash
pip install -e .
```

## Project Structure

```
LE-Slider-IO/
├── src/le_slider_io/
│   ├── __init__.py           # Package exports
│   ├── schema.py             # RatingRecordingSchema dataclass
│   └── recording.py          # Recording utilities
├── test/
│   ├── conftest.py           # Pytest fixtures
│   ├── test_schema.py        # Schema serialization tests
│   └── test_recording.py     # Recording utility tests
├── pyproject.toml            # Project configuration
├── README.md                 # This file
└── LICENSE                   # GPLv3 license
```
___

# Quick Start

## Basic Usage: Create and Save a Recording

```python
from le_slider_io import RatingRecordingSchema, save_recording

# Create a recording schema
schema = RatingRecordingSchema(
    participant_id="VP001",
    session_id="2026-04-27T10:00:00+02:00",
    stimulus_path="/path/to/audio.wav",
    stimulus_list="ExperimentList.txt",
    stimulus_start="2026-04-27T10:00:01+02:00",
    stimulus_end="2026-04-27T10:00:05+02:00",
    slider_config={"min": 0, "max": 10, "label": "Listening Effort"},
    ratings=[5.0, 5.5, 6.0, 5.8, 5.2],
    time_stamps=[0.010, 0.020, 0.030, 0.040, 0.050]
)

# Save to JSON file (creates directories automatically)
filepath = save_recording(schema, output_dir="results/")
print(f"Saved to: {filepath}")
# Output: Saved to: /absolute/path/to/results/VP001_audio.json
```

## Load a Recording

```python
from le_slider_io import load_recording

schema = load_recording("results/VP001_audio.json")
print(f"Participant: {schema.participant_id}")
print(f"Ratings: {schema.ratings}")
print(f"Timestamps: {schema.time_stamps}")
```

## Calculate Timestamps Automatically

```python
from le_slider_io import calculate_relative_timestamps

# Calculate timestamps based on audio processing parameters
# num_samples: number of ratings collected
# blocksize: audio frames per callback
# sample_rate: Hz
timestamps = calculate_relative_timestamps(
    num_samples=100,
    blocksize=512,
    sample_rate=44100
)
print(f"Generated {len(timestamps)} timestamps")
```

## Batch Load Recordings

```python
from le_slider_io import load_all_recordings

# Load all .json files from directory (searches recursively)
recordings = load_all_recordings("results/")
print(f"Loaded {len(recordings)} recordings")

for schema in recordings:
    print(f"  - {schema.participant_id}: {len(schema.ratings)} ratings")
```

## Manual JSON Serialization

```python
from le_slider_io import RatingRecordingSchema

schema = RatingRecordingSchema(participant_id="VP001")

# Convert to dictionary
data_dict = schema.to_json_dict()

# Convert to formatted JSON string
json_string = schema.to_json_string(indent=2)
print(json_string)

# Load from dictionary
loaded = RatingRecordingSchema.from_json_dict(data_dict)

# Load from JSON file
loaded = RatingRecordingSchema.from_json_file("path/to/file.json")
```

## JSON Output Format

Example output file from `schema.to_json_file()`:

```json
{
  "session_id": "2026-04-27T10:00:00+02:00",
  "participant_id": "VP001",
  "stimulus_path": "/path/to/audio.wav",
  "stimulus_list": "ExperimentList.txt",
  "stimulus_start": "2026-04-27T10:00:01+02:00",
  "stimulus_end": "2026-04-27T10:00:05+02:00",
  "slider_config": {
    "min": 0,
    "max": 10,
    "step": 0.1,
    "label": "Listening Effort"
  },
  "ratings": [5.0, 5.5, 6.0, 5.8, 5.2],
  "time_stamps": [0.010, 0.020, 0.030, 0.040, 0.050]
}
```

___

# API Reference

## RatingRecordingSchema

A dataclass containing all metadata and ratings for a single recording session.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `session_id` | str | "" | Unique session identifier (typically ISO timestamp) |
| `participant_id` | str | "" | Participant or subject identifier |
| `stimulus_path` | str | "" | Full path to the audio stimulus file |
| `stimulus_list` | str | "" | Name of stimulus list |
| `stimulus_start` | str | "" | ISO timestamp when stimulus playback started |
| `stimulus_end` | str | "" | ISO timestamp when stimulus playback ended |
| `slider_config` | Dict[str, Any] | {} | Slider configuration (min, max, step, label, etc.) |
| `ratings` | list | [] | Array of slider values collected during stimulus |
| `time_stamps` | list | [] | Array of relative timestamps in seconds |

### Methods

**`to_json_dict() -> Dict[str, Any]`**
- Converts schema to JSON-serializable dictionary

**`to_json_string(indent: int = 2) -> str`**
- Converts schema to formatted JSON string
- `indent`: Number of spaces per indentation level (None for compact)

**`to_json_file(filepath: str, indent: int = 2) -> None`**
- Saves schema to JSON file
- Creates directories if they don't exist
- Raises `OSError` if file cannot be written

**`from_json_dict(data: Dict[str, Any]) -> RatingRecordingSchema`** (static)
- Creates schema instance from dictionary
- Raises `KeyError` if required fields are missing

**`from_json_file(filepath: str) -> RatingRecordingSchema`** (static)
- Creates schema instance from JSON file
- Raises `FileNotFoundError` if file doesn't exist
- Raises `json.JSONDecodeError` if JSON is invalid

## Recording Utilities

**`calculate_relative_timestamps(num_samples: int, blocksize: int, sample_rate: int) -> List[float]`**
- Calculates evenly-spaced relative timestamps
- Returns list of timestamps in seconds
- Returns empty list if any parameter is ≤ 0

**`save_recording(schema: RatingRecordingSchema, output_dir: str, naming_template: str = "{participant_id}_{stimulus_name}.json") -> str`**
- Saves schema to JSON file in output directory
- `naming_template`: Template for filename generation
  - Available fields: `{participant_id}`, `{stimulus_name}`, `{session_id}`
  - `{stimulus_name}` is the basename of `stimulus_path` without extension
- Returns absolute path to saved file

**`load_recording(filepath: str) -> RatingRecordingSchema`**
- Loads schema from JSON file
- Raises `FileNotFoundError` if file doesn't exist
- Raises `json.JSONDecodeError` if JSON is invalid
- Raises `KeyError` if required fields are missing

**`load_all_recordings(directory: str) -> List[RatingRecordingSchema]`**
- Loads all .json files from directory recursively
- Skips files that cannot be parsed as recordings
- Returns empty list if directory doesn't exist or contains no valid files
___

# License

GNU General Public License v3.0 or later (GPLv3+)
___

# Acknowledgements
This project was created with the assistance of **GitHub Copilot** with **Claude Haiku 4.5** as the underlying language model to make the slider code from the original publication a flexible standalone application.
___

# Citation
If you use this toolbox in research, please cite:
```bibtex
@article{berdau2026blind,
  title={A blind binaural real-time model for listening effort evaluated using continuous subjective listening effort rating},
  author={Berdau, Martin and Padilla, Daniel-Jos{\'e} Alcala and Brand, Thomas and Rollwage, Christian and Rennies, Jan},
  journal={Acta Acustica},
  volume={10},
  pages={11},
  year={2026},
  publisher={EDP Sciences}
}
```