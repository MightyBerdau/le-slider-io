"""Tests for recording utilities."""

import os
import json
import pytest
from pathlib import Path
from le_slider_io.schema import RatingRecordingSchema
from le_slider_io.recording import (
    calculate_relative_timestamps,
    save_recording,
    load_recording,
    load_all_recordings,
    get_safe_filepath
)


class TestCalculateRelativeTimestamps:
    """Test timestamp calculation for audio playback."""
    
    def test_calculate_timestamps_basic(self):
        """Verify basic timestamp calculation."""
        timestamps = calculate_relative_timestamps(
            num_samples=10,
            blocksize=1024,
            sample_rate=44100
        )
        assert len(timestamps) == 10
        assert all(isinstance(t, float) for t in timestamps)
    
    def test_calculate_timestamps_monotonic_increasing(self):
        """Verify timestamps are monotonically increasing."""
        timestamps = calculate_relative_timestamps(
            num_samples=5,
            blocksize=512,
            sample_rate=48000
        )
        for i in range(len(timestamps) - 1):
            assert timestamps[i] < timestamps[i + 1]
    
    def test_calculate_timestamps_values(self):
        """Verify timestamp values are correct."""
        # At 44100 Hz with 1024 blocksize:
        # Sample 0: (0+1) * 1024 / 44100 = 1024/44100 ≈ 0.02322675...
        timestamps = calculate_relative_timestamps(
            num_samples=3,
            blocksize=1024,
            sample_rate=44100
        )
        assert len(timestamps) == 3
        expected_first = 1024 / 44100
        assert abs(timestamps[0] - expected_first) < 0.0001
    
    def test_calculate_timestamps_zero_samples(self):
        """Verify behavior with zero samples."""
        timestamps = calculate_relative_timestamps(
            num_samples=0,
            blocksize=1024,
            sample_rate=44100
        )
        assert timestamps == []
    
    def test_calculate_timestamps_negative_values_returns_empty(self):
        """Verify negative parameters return empty list."""
        assert calculate_relative_timestamps(-1, 1024, 44100) == []
        assert calculate_relative_timestamps(10, -1024, 44100) == []
        assert calculate_relative_timestamps(10, 1024, -44100) == []
        assert calculate_relative_timestamps(0, 0, 0) == []
    
    def test_calculate_timestamps_different_sample_rates(self):
        """Verify timestamps scale correctly with sample rate."""
        timestamps_44k = calculate_relative_timestamps(10, 1024, 44100)
        timestamps_48k = calculate_relative_timestamps(10, 1024, 48000)
        
        # 48kHz should have shorter timestamps (sample-accurate)
        assert timestamps_48k[0] < timestamps_44k[0]
    
    def test_calculate_timestamps_different_blocksizes(self):
        """Verify timestamps scale correctly with blocksize."""
        timestamps_512 = calculate_relative_timestamps(10, 512, 44100)
        timestamps_2048 = calculate_relative_timestamps(10, 2048, 44100)
        
        # Larger blocksize means longer intervals between samples
        assert timestamps_2048[0] > timestamps_512[0]


class TestGetSafeFilepath:
    """Test file collision prevention utility."""
    
    def test_safe_filepath_no_collision(self, temp_output_dir):
        """Verify returns original path when file doesn't exist."""
        filepath = os.path.join(temp_output_dir, "new_file.json")
        result = get_safe_filepath(filepath)
        assert result == filepath
    
    def test_safe_filepath_with_collision(self, temp_output_dir):
        """Verify generates _1 suffix when file exists."""
        filepath = os.path.join(temp_output_dir, "data.json")
        # Create the file
        with open(filepath, 'w') as f:
            f.write("{}")
        
        result = get_safe_filepath(filepath)
        assert result.endswith("data_1.json")
        assert os.path.dirname(result) == temp_output_dir
        assert not os.path.exists(result)  # Should return a path that doesn't exist
    
    def test_safe_filepath_multiple_collisions(self, temp_output_dir):
        """Verify increments counter when multiple variants exist."""
        filepath = os.path.join(temp_output_dir, "data.json")
        # Create original and first variant
        with open(filepath, 'w') as f:
            f.write("{}")
        with open(os.path.join(temp_output_dir, "data_1.json"), 'w') as f:
            f.write("{}")
        
        result = get_safe_filepath(filepath)
        assert result.endswith("data_2.json")
        assert not os.path.exists(result)
    
    def test_safe_filepath_with_multiple_dots(self, temp_output_dir):
        """Verify handles filenames with multiple dots correctly."""
        filepath = os.path.join(temp_output_dir, "data.backup.json")
        with open(filepath, 'w') as f:
            f.write("{}")
        
        result = get_safe_filepath(filepath)
        assert result.endswith("data.backup_1.json")
        # Extension should be preserved
        assert result.startswith(os.path.join(temp_output_dir, "data.backup_"))
    
    def test_safe_filepath_no_extension(self, temp_output_dir):
        """Verify handles files without extensions."""
        filepath = os.path.join(temp_output_dir, "datafile")
        with open(filepath, 'w') as f:
            f.write("{}")
        
        result = get_safe_filepath(filepath)
        assert result.endswith("datafile_1")
        assert not os.path.exists(result)
    
    def test_safe_filepath_high_counter(self, temp_output_dir):
        """Verify handles high counter values efficiently."""
        filepath = os.path.join(temp_output_dir, "data.json")
        # Create files up to _5
        with open(filepath, 'w') as f:
            f.write("{}")
        for i in range(1, 6):
            with open(os.path.join(temp_output_dir, f"data_{i}.json"), 'w') as f:
                f.write("{}")
        
        result = get_safe_filepath(filepath)
        assert result.endswith("data_6.json")
    
    def test_safe_filepath_with_nested_dirs(self):
        """Verify handles nested directory paths."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            nested_dir = os.path.join(tmp, "level1", "level2", "level3")
            os.makedirs(nested_dir, exist_ok=True)
            
            filepath = os.path.join(nested_dir, "data.json")
            with open(filepath, 'w') as f:
                f.write("{}")
            
            result = get_safe_filepath(filepath)
            assert result.endswith("data_1.json")
            assert os.path.dirname(result) == nested_dir


class TestSaveRecording:
    """Test saving RatingRecordingSchema to file."""
    
    def test_save_recording_creates_file(self, sample_schema, temp_output_dir):
        """Verify save_recording creates a file."""
        filepath = save_recording(sample_schema, temp_output_dir)
        assert os.path.exists(filepath)
        assert filepath.endswith(".json")
    
    def test_save_recording_returns_absolute_path(self, sample_schema, temp_output_dir):
        """Verify save_recording returns absolute filepath."""
        filepath = save_recording(sample_schema, temp_output_dir)
        assert os.path.isabs(filepath)
    
    def test_save_recording_default_naming_template(self, sample_schema, temp_output_dir):
        """Verify default naming template produces correct filename."""
        filepath = save_recording(sample_schema, temp_output_dir)
        # Default template: {participant_id}_{stimulus_name}.json
        # stimulus_name should be "S0N180_headrot_short" (without .wav)
        assert "VP001_S0N180_headrot_short.json" in filepath
    
    def test_save_recording_custom_naming_template(self, sample_schema, temp_output_dir):
        """Verify custom naming template is used."""
        # Use a template that's valid on Windows (no colons)
        template = "recording_{stimulus_name}.json"
        filepath = save_recording(
            sample_schema,
            temp_output_dir,
            naming_template=template
        )
        # Should use the custom template format
        assert "recording_S0N180_headrot_short.json" in filepath
    
    def test_save_recording_creates_directories(self, sample_schema):
        """Verify save_recording creates nested directories."""
        nested_dir = "/tmp/nested/deep/test/dir"
        # Use a temp directory instead of /tmp for cross-platform testing
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            nested_path = os.path.join(tmp, "nested", "deep", "test", "dir")
            filepath = save_recording(sample_schema, nested_path)
            assert os.path.exists(filepath)
            assert os.path.isdir(nested_path)
    
    def test_save_recording_file_content_valid_json(self, sample_schema, temp_output_dir):
        """Verify saved file contains valid JSON."""
        filepath = save_recording(sample_schema, temp_output_dir)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data["participant_id"] == "VP001"
        assert data["ratings"] == sample_schema.ratings
    
    def test_save_recording_preserves_schema_data(self, sample_schema, temp_output_dir):
        """Verify all schema data is preserved in saved file."""
        filepath = save_recording(sample_schema, temp_output_dir)
        loaded = load_recording(filepath)
        
        assert loaded.participant_id == sample_schema.participant_id
        assert loaded.session_id == sample_schema.session_id
        assert loaded.stimulus_path == sample_schema.stimulus_path
        assert loaded.stimulus_list == sample_schema.stimulus_list
        assert loaded.ratings == sample_schema.ratings
        assert loaded.time_stamps == sample_schema.time_stamps
        assert loaded.slider_config == sample_schema.slider_config
    
    def test_save_recording_with_empty_stimulus_path(self, temp_output_dir):
        """Verify save_recording handles empty stimulus_path gracefully."""
        schema = RatingRecordingSchema(
            participant_id="VP001",
            stimulus_path="",
            ratings=[5.0, 5.5]
        )
        filepath = save_recording(schema, temp_output_dir)
        assert os.path.exists(filepath)
        # Filename should be VP001_.json (empty stimulus name)
        assert "VP001_" in filepath
    
    def test_save_recording_prevent_overwrite_enabled(self, sample_schema, temp_output_dir):
        """Verify save_recording creates unique filename when prevent_overwrite=True."""
        # Save same schema twice
        filepath1 = save_recording(sample_schema, temp_output_dir, prevent_overwrite=True)
        filepath2 = save_recording(sample_schema, temp_output_dir, prevent_overwrite=True)
        
        # Second save should have _1 suffix
        assert filepath1 != filepath2
        assert "_1" in filepath2
        assert os.path.exists(filepath1)
        assert os.path.exists(filepath2)
        
        # Both should contain valid data
        data1 = json.load(open(filepath1))
        data2 = json.load(open(filepath2))
        assert data1["participant_id"] == data2["participant_id"]
    
    def test_save_recording_prevent_overwrite_disabled(self, temp_output_dir):
        """Verify save_recording overwrites when prevent_overwrite=False."""
        # Create initial schema
        schema = RatingRecordingSchema(
            participant_id="VP001",
            stimulus_path="stimulus.wav",
            ratings=[1.0, 2.0]
        )
        
        # Save first time
        filepath1 = save_recording(schema, temp_output_dir, prevent_overwrite=False)
        
        # Verify file exists with initial content
        with open(filepath1) as f:
            data1 = json.load(f)
        assert data1["ratings"] == [1.0, 2.0]
        
        # Modify ratings and save again to same location (should overwrite)
        schema.ratings = [3.0, 4.0, 5.0]
        filepath2 = save_recording(schema, temp_output_dir, prevent_overwrite=False)
        
        # Both should return same filepath
        assert filepath1 == filepath2
        
        # File should contain updated data (overwritten)
        with open(filepath2) as f:
            data2 = json.load(f)
        assert data2["ratings"] == [3.0, 4.0, 5.0]
    
    def test_save_recording_prevent_overwrite_default(self, sample_schema, temp_output_dir):
        """Verify prevent_overwrite=True is the default."""
        # Save without specifying prevent_overwrite (should default to True)
        filepath1 = save_recording(sample_schema, temp_output_dir)
        filepath2 = save_recording(sample_schema, temp_output_dir)
        
        # Second should have _1 suffix (collision prevented)
        assert filepath1 != filepath2
        assert "_1" in filepath2


class TestLoadRecording:
    """Test loading RatingRecordingSchema from file."""
    
    def test_load_recording_basic(self, sample_json_file):
        """Verify load_recording loads schema from file."""
        schema = load_recording(sample_json_file)
        assert isinstance(schema, RatingRecordingSchema)
        assert schema.participant_id == "VP001"
    
    def test_load_recording_round_trip(self, sample_schema, temp_output_dir):
        """Verify round-trip: save → load returns identical schema."""
        filepath = save_recording(sample_schema, temp_output_dir)
        loaded = load_recording(filepath)
        
        assert loaded.participant_id == sample_schema.participant_id
        assert loaded.session_id == sample_schema.session_id
        assert loaded.stimulus_path == sample_schema.stimulus_path
        assert loaded.ratings == sample_schema.ratings
        assert loaded.slider_config == sample_schema.slider_config
    
    def test_load_recording_file_not_found(self):
        """Verify load_recording raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_recording("/nonexistent/path/file.json")
    
    def test_load_recording_invalid_json(self, temp_output_dir):
        """Verify load_recording raises JSONDecodeError for invalid JSON."""
        filepath = os.path.join(temp_output_dir, "invalid.json")
        with open(filepath, 'w') as f:
            f.write("not valid json {")
        
        with pytest.raises(json.JSONDecodeError):
            load_recording(filepath)
    
    def test_load_recording_missing_required_field(self, temp_output_dir):
        """Verify load_recording raises KeyError for missing required fields."""
        filepath = os.path.join(temp_output_dir, "incomplete.json")
        with open(filepath, 'w') as f:
            json.dump({"participant_id": "VP001"}, f)
        
        with pytest.raises(KeyError):
            load_recording(filepath)


class TestLoadAllRecordings:
    """Test batch loading of recordings from directory."""
    
    def test_load_all_recordings_empty_directory(self):
        """Verify load_all_recordings returns empty list for empty dir."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            recordings = load_all_recordings(tmp)
            assert recordings == []
    
    def test_load_all_recordings_nonexistent_directory(self):
        """Verify load_all_recordings returns empty list for missing dir."""
        recordings = load_all_recordings("/nonexistent/path/that/does/not/exist")
        assert recordings == []
    
    def test_load_all_recordings_single_file(self, sample_json_file, temp_output_dir):
        """Verify load_all_recordings finds single recording."""
        # Sample file is already in temp_output_dir
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            # Create a sample file
            schema = RatingRecordingSchema(
                participant_id="VP001",
                stimulus_path="test.wav",
                ratings=[5.0]
            )
            save_recording(schema, tmp)
            
            recordings = load_all_recordings(tmp)
            assert len(recordings) == 1
            assert recordings[0].participant_id == "VP001"
    
    def test_load_all_recordings_multiple_files(self, temp_output_dir):
        """Verify load_all_recordings finds multiple recordings."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            # Create multiple recordings
            for i in range(3):
                schema = RatingRecordingSchema(
                    participant_id=f"VP{i:03d}",
                    stimulus_path=f"test{i}.wav",
                    ratings=[5.0]
                )
                save_recording(schema, tmp)
            
            recordings = load_all_recordings(tmp)
            assert len(recordings) == 3
            participant_ids = {r.participant_id for r in recordings}
            assert participant_ids == {"VP000", "VP001", "VP002"}
    
    def test_load_all_recordings_nested_directories(self, temp_output_dir):
        """Verify load_all_recordings finds files in nested directories."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            # Create recordings in nested dirs
            schema = RatingRecordingSchema(
                participant_id="VP001",
                stimulus_path="test.wav",
                ratings=[5.0]
            )
            nested_dir = os.path.join(tmp, "sub1", "sub2")
            save_recording(schema, nested_dir)
            
            recordings = load_all_recordings(tmp)
            assert len(recordings) == 1
            assert recordings[0].participant_id == "VP001"
    
    def test_load_all_recordings_skips_invalid_files(self, temp_output_dir):
        """Verify load_all_recordings skips unparseable JSON files."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            # Create one valid recording
            schema = RatingRecordingSchema(
                participant_id="VP001",
                stimulus_path="test.wav",
                ratings=[5.0]
            )
            save_recording(schema, tmp)
            
            # Create one invalid JSON file
            invalid_path = os.path.join(tmp, "invalid.json")
            with open(invalid_path, 'w') as f:
                f.write("not valid json")
            
            # Should load the valid one and skip the invalid
            recordings = load_all_recordings(tmp)
            assert len(recordings) == 1
            assert recordings[0].participant_id == "VP001"


class TestIntegration:
    """Integration tests combining multiple functions."""
    
    def test_full_workflow(self, temp_output_dir):
        """Test complete workflow: create → save → load → verify."""
        # Create schema
        schema = RatingRecordingSchema(
            participant_id="VP001",
            session_id="2026-04-27T10:00:00+02:00",
            stimulus_path="C:\\Audio\\test_stimulus.wav",
            stimulus_list="TestList.txt",
            stimulus_start="2026-04-27T10:00:01+02:00",
            stimulus_end="2026-04-27T10:00:05+02:00",
            slider_config={"min": 0, "max": 10},
            ratings=[5.0, 5.5, 6.0, 5.8],
            time_stamps=[0.01, 0.02, 0.03, 0.04]
        )
        
        # Save
        filepath = save_recording(schema, temp_output_dir)
        assert os.path.exists(filepath)
        
        # Load
        loaded = load_recording(filepath)
        
        # Verify
        assert loaded.participant_id == "VP001"
        assert loaded.ratings == [5.0, 5.5, 6.0, 5.8]
        assert loaded.slider_config == {"min": 0, "max": 10}
    
    def test_workflow_with_timestamps(self):
        """Test workflow including timestamp calculation."""
        num_samples = 100
        blocksize = 512
        sample_rate = 44100
        
        # Calculate timestamps
        timestamps = calculate_relative_timestamps(num_samples, blocksize, sample_rate)
        
        # Create schema with calculated timestamps
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            schema = RatingRecordingSchema(
                participant_id="VP001",
                stimulus_path="test.wav",
                ratings=[5.0] * num_samples,
                time_stamps=timestamps
            )
            
            # Save and load
            filepath = save_recording(schema, tmp)
            loaded = load_recording(filepath)
            
            # Verify timestamps preserved
            assert len(loaded.time_stamps) == num_samples
            assert loaded.time_stamps == timestamps
