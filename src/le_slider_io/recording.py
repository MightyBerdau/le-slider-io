"""Recording utilities for saving RatingRecordingSchema to JSON files.

This module provides utilities for handling rating recordings, including
timestamp calculation and file persistence.
"""

import os
from pathlib import Path
from typing import List
from .schema import RatingRecordingSchema


def calculate_relative_timestamps(
    num_samples: int,
    blocksize: int,
    sample_rate: int
) -> List[float]:
    """Calculate relative timestamps for recorded samples.
    
    Generates a list of timestamps representing when each rating sample
    was recorded, relative to the start of playback in seconds.
    
    Args:
        num_samples: Number of rating samples collected
        blocksize: Number of audio frames processed per callback
        sample_rate: Sample rate in Hz (samples per second)
    
    Returns:
        List of timestamps in seconds, one per sample
        
    Example:
        >>> calculate_relative_timestamps(10, 1024, 44100)
        [0.023219..., 0.046439..., ...]  # ~10 timestamps
    """
    if num_samples <= 0 or blocksize <= 0 or sample_rate <= 0:
        return []
    
    # Each sample corresponds to (ii+1) * blocksize / sample_rate seconds
    return [(ii + 1) * blocksize / sample_rate for ii in range(num_samples)]


def save_recording(
    schema: RatingRecordingSchema,
    output_dir: str,
    naming_template: str = "{participant_id}_{stimulus_name}.json"
) -> str:
    """Save a RatingRecordingSchema to a JSON file.
    
    Creates necessary output directories and saves the schema as a formatted
    JSON file. Filename is generated from the template and schema fields.
    
    Args:
        schema: RatingRecordingSchema instance to save
        output_dir: Directory path where JSON file will be created
        naming_template: Filename template with available fields:
            - {participant_id}: schema.participant_id
            - {stimulus_name}: basename of stimulus_path (without extension)
            - {session_id}: schema.session_id (default: not used)
    
    Returns:
        Absolute path to the saved JSON file
        
    Raises:
        OSError: If file cannot be written
        ValueError: If required fields are missing in schema
        
    Example:
        >>> schema = RatingRecordingSchema(
        ...     participant_id="VP001",
        ...     stimulus_path="/path/to/stimulus.wav",
        ...     ratings=[5.0, 5.5, 6.0],
        ...     time_stamps=[0.01, 0.02, 0.03]
        ... )
        >>> filepath = save_recording(schema, "results/")
        >>> print(filepath)
        /path/to/results/VP001_stimulus.json
    """
    # Extract stimulus basename without extension
    stimulus_name = os.path.splitext(
        os.path.basename(schema.stimulus_path)
    )[0]
    
    # Generate filename from template
    filename = naming_template.format(
        participant_id=schema.participant_id,
        stimulus_name=stimulus_name,
        session_id=schema.session_id
    )
    
    # Construct full filepath
    filepath = os.path.join(output_dir, filename)
    
    # Save using schema's built-in method (handles directory creation)
    schema.to_json_file(filepath)
    
    return os.path.abspath(filepath)


def load_recording(filepath: str) -> RatingRecordingSchema:
    """Load a RatingRecordingSchema from a JSON file.
    
    Args:
        filepath: Path to JSON file containing recording data
        
    Returns:
        RatingRecordingSchema instance
        
    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If file is not valid JSON
        KeyError: If required fields are missing in JSON
        
    Example:
        >>> schema = load_recording("results/VP001_stimulus.json")
        >>> print(schema.participant_id)
        VP001
    """
    return RatingRecordingSchema.from_json_file(filepath)


def load_all_recordings(directory: str) -> List[RatingRecordingSchema]:
    """Load all RatingRecordingSchema JSON files from a directory.
    
    Recursively searches the directory for all .json files and attempts
    to load them as RatingRecordingSchema instances.
    
    Args:
        directory: Directory path to search for JSON files
        
    Returns:
        List of successfully loaded RatingRecordingSchema instances
        
    Example:
        >>> schemas = load_all_recordings("results/")
        >>> print(f"Loaded {len(schemas)} recordings")
        Loaded 5 recordings
    """
    recordings = []
    directory_path = Path(directory)
    
    if not directory_path.exists():
        return recordings
    
    for json_file in directory_path.rglob("*.json"):
        try:
            schema = load_recording(str(json_file))
            recordings.append(schema)
        except Exception:
            # Skip files that cannot be loaded as recordings
            continue
    
    return recordings
