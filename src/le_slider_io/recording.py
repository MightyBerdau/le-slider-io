"""Recording utilities for saving RatingRecordingSchema to JSON files.

This module provides utilities for handling rating recordings, including
timestamp calculation and file persistence.
"""

import os
from pathlib import Path
from typing import List
from .schema import RatingRecordingSchema


def get_safe_filepath(filepath: str) -> str:
    """Generate a safe filepath that doesn't overwrite existing files.
    
    If the file doesn't exist, returns the original filepath.
    If it exists, generates alternatives with numeric suffixes before the extension
    (e.g., 'file_1.json', 'file_2.json') until an unused name is found.
    
    Args:
        filepath: Path to the desired file
        
    Returns:
        A filepath that is guaranteed not to exist (safe to write to)
        
    Example:
        >>> # If 'data.json' exists but 'data_1.json' doesn't:
        >>> get_safe_filepath('/path/to/data.json')
        '/path/to/data_1.json'
    """
    if not os.path.exists(filepath):
        return filepath
    
    # Split filepath into directory, name, and extension
    directory = os.path.dirname(filepath) or '.'
    filename = os.path.basename(filepath)
    
    # Handle files with extensions
    if '.' in filename:
        name_parts = filename.rsplit('.', 1)
        base_name = name_parts[0]
        extension = '.' + name_parts[1]
    else:
        base_name = filename
        extension = ''
    
    # Find the next available filename by incrementing counter
    counter = 1
    while True:
        new_filename = f"{base_name}_{counter}{extension}"
        new_filepath = os.path.join(directory, new_filename)
        if not os.path.exists(new_filepath):
            return new_filepath
        counter += 1


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
    naming_template: str = "{participant_id}_{stimulus_name}.json",
    prevent_overwrite: bool = True
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
        prevent_overwrite: If True (default), appends numeric suffix to avoid
            overwriting existing files (e.g., 'file_1.json')
    
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
    
    # Save using schema's built-in method (handles directory creation and collision prevention)
    # Returns the actual filepath that was written (may differ if collision prevention is enabled)
    actual_filepath = schema.to_json_file(filepath, prevent_overwrite=prevent_overwrite)
    
    return actual_filepath


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
