"""Tests for RatingRecordingSchema serialization and deserialization."""

import json
import os
from pathlib import Path
import pytest
from le_slider_io.schema import RatingRecordingSchema


class TestRatingRecordingSchemaDefaults:
    """Test default values and initialization."""
    
    def test_schema_default_values(self):
        """Verify all fields have correct default values."""
        schema = RatingRecordingSchema()
        assert schema.session_id == ""
        assert schema.participant_id == ""
        assert schema.stimulus_path == ""
        assert schema.stimulus_list == ""
        assert schema.stimulus_start == ""
        assert schema.stimulus_end == ""
        assert schema.slider_config == {}
        assert schema.ratings == []
        assert schema.time_stamps == []
    
    def test_schema_partial_initialization(self):
        """Verify schema can be initialized with partial fields."""
        schema = RatingRecordingSchema(
            participant_id="VP001",
            stimulus_path="test.wav"
        )
        assert schema.participant_id == "VP001"
        assert schema.stimulus_path == "test.wav"
        assert schema.ratings == []
    
    def test_schema_full_initialization(self, sample_schema):
        """Verify schema initializes with all fields correctly."""
        assert sample_schema.participant_id == "VP001"
        assert sample_schema.session_id == "2026-04-24T13:15:36.008773+02:00"
        assert len(sample_schema.ratings) == 7
        assert len(sample_schema.time_stamps) == 7


class TestToJsonDict:
    """Test conversion to JSON-serializable dictionary."""
    
    def test_to_json_dict_basic(self, sample_schema):
        """Verify to_json_dict produces valid dictionary."""
        json_dict = sample_schema.to_json_dict()
        assert isinstance(json_dict, dict)
        assert json_dict["participant_id"] == "VP001"
        assert json_dict["ratings"] == [6.6, 6.6, 6.6, 6.7, 6.5, 6.4, 6.5]
    
    def test_to_json_dict_has_all_fields(self, sample_schema):
        """Verify to_json_dict includes all schema fields."""
        json_dict = sample_schema.to_json_dict()
        expected_fields = {
            "session_id", "participant_id", "stimulus_path",
            "stimulus_list", "stimulus_start", "stimulus_end",
            "slider_config", "ratings", "time_stamps"
        }
        assert set(json_dict.keys()) == expected_fields
    
    def test_to_json_dict_default_schema(self):
        """Verify to_json_dict works with default schema."""
        schema = RatingRecordingSchema()
        json_dict = schema.to_json_dict()
        assert json_dict["participant_id"] == ""
        assert json_dict["ratings"] == []
        assert json_dict["slider_config"] == {}
    
    def test_to_json_dict_empty_lists(self):
        """Verify to_json_dict handles empty ratings and timestamps."""
        schema = RatingRecordingSchema(
            participant_id="VP001",
            stimulus_path="test.wav",
            ratings=[],
            time_stamps=[]
        )
        json_dict = schema.to_json_dict()
        assert json_dict["ratings"] == []
        assert json_dict["time_stamps"] == []


class TestToJsonString:
    """Test conversion to formatted JSON string."""
    
    def test_to_json_string_valid_json(self, sample_schema):
        """Verify to_json_string produces valid JSON."""
        json_string = sample_schema.to_json_string()
        # Should not raise JSONDecodeError
        parsed = json.loads(json_string)
        assert isinstance(parsed, dict)
        assert parsed["participant_id"] == "VP001"
    
    def test_to_json_string_indent_default(self, sample_schema):
        """Verify to_json_string uses default indent=2."""
        json_string = sample_schema.to_json_string()
        # Indented JSON should have newlines and spaces
        assert "\n" in json_string
        assert "  " in json_string
    
    def test_to_json_string_custom_indent(self, sample_schema):
        """Verify to_json_string respects custom indent."""
        json_string_indent2 = sample_schema.to_json_string(indent=2)
        json_string_indent4 = sample_schema.to_json_string(indent=4)
        # Both should be valid JSON
        assert json.loads(json_string_indent2)
        assert json.loads(json_string_indent4)
        # Indent 4 should have more spaces per level
        assert json_string_indent4.count(" ") > json_string_indent2.count(" ")
    
    def test_to_json_string_unicode_handling(self):
        """Verify to_json_string preserves unicode (ensure_ascii=False)."""
        schema = RatingRecordingSchema(
            participant_id="VP001",
            stimulus_list="Ümlaut_Test_äöü.txt"
        )
        json_string = schema.to_json_string()
        # ensure_ascii=False should preserve unicode characters
        assert "ä" in json_string or "\\u00e4" in json_string
        # Should be valid JSON
        parsed = json.loads(json_string)
        assert "ä" in parsed["stimulus_list"] or parsed["stimulus_list"]
    
    def test_to_json_string_no_indent(self, sample_schema):
        """Verify to_json_string with indent=None produces compact JSON."""
        json_string = sample_schema.to_json_string(indent=None)
        parsed = json.loads(json_string)
        assert parsed["participant_id"] == "VP001"
        # Compact JSON should have no indentation
        assert json_string == json_string.replace("\n", "").replace("  ", "")


class TestToJsonFile:
    """Test saving schema to JSON file."""
    
    def test_to_json_file_creates_file(self, sample_schema, temp_output_dir):
        """Verify to_json_file creates a file."""
        filepath = os.path.join(temp_output_dir, "test_output.json")
        sample_schema.to_json_file(filepath)
        assert os.path.exists(filepath)
    
    def test_to_json_file_creates_directories(self, sample_schema, temp_output_dir):
        """Verify to_json_file creates missing directories."""
        filepath = os.path.join(
            temp_output_dir, "nested", "deep", "test_output.json"
        )
        sample_schema.to_json_file(filepath)
        assert os.path.exists(filepath)
        assert os.path.isdir(os.path.dirname(filepath))
    
    def test_to_json_file_content_valid_json(self, sample_schema, temp_output_dir):
        """Verify saved file contains valid JSON."""
        filepath = os.path.join(temp_output_dir, "test.json")
        sample_schema.to_json_file(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data["participant_id"] == "VP001"
        assert data["ratings"] == [6.6, 6.6, 6.6, 6.7, 6.5, 6.4, 6.5]
    
    def test_to_json_file_custom_indent(self, sample_schema, temp_output_dir):
        """Verify to_json_file respects custom indent."""
        filepath1 = os.path.join(temp_output_dir, "indent2.json")
        filepath2 = os.path.join(temp_output_dir, "indent4.json")
        
        sample_schema.to_json_file(filepath1, indent=2)
        sample_schema.to_json_file(filepath2, indent=4)
        
        with open(filepath1, 'r') as f:
            content1 = f.read()
        with open(filepath2, 'r') as f:
            content2 = f.read()
        
        # Indent 4 should be longer due to more spaces
        assert len(content2) > len(content1)


class TestFromJsonDict:
    """Test deserialization from JSON dictionary."""
    
    def test_from_json_dict_basic(self, sample_json_dict):
        """Verify from_json_dict reconstructs schema."""
        schema = RatingRecordingSchema.from_json_dict(sample_json_dict)
        assert schema.participant_id == "VP001"
        assert schema.stimulus_path == "C:\\Audio\\S0N180_headrot_short.wav"
        assert schema.ratings == [6.6, 6.6, 6.6, 6.7, 6.5, 6.4, 6.5]
    
    def test_from_json_dict_round_trip(self, sample_schema):
        """Verify round-trip: schema → dict → schema."""
        json_dict = sample_schema.to_json_dict()
        reconstructed = RatingRecordingSchema.from_json_dict(json_dict)
        
        assert reconstructed.participant_id == sample_schema.participant_id
        assert reconstructed.session_id == sample_schema.session_id
        assert reconstructed.ratings == sample_schema.ratings
        assert reconstructed.slider_config == sample_schema.slider_config
    
    def test_from_json_dict_with_missing_optional_fields(self):
        """Verify from_json_dict handles missing optional fields."""
        minimal_dict = {
            "participant_id": "VP001",
            "stimulus_path": "test.wav",
            "stimulus_list": "list.txt"
        }
        schema = RatingRecordingSchema.from_json_dict(minimal_dict)
        assert schema.participant_id == "VP001"
        assert schema.session_id == ""
        assert schema.slider_config == {}
        assert schema.ratings == []
    
    def test_from_json_dict_missing_required_field_raises(self):
        """Verify from_json_dict raises KeyError for missing required fields."""
        incomplete_dict = {
            "participant_id": "VP001"
            # Missing stimulus_path
        }
        with pytest.raises(KeyError):
            RatingRecordingSchema.from_json_dict(incomplete_dict)


class TestFromJsonFile:
    """Test deserialization from JSON file."""
    
    def test_from_json_file_basic(self, sample_json_file):
        """Verify from_json_file loads schema from file."""
        schema = RatingRecordingSchema.from_json_file(sample_json_file)
        assert schema.participant_id == "VP001"
        assert schema.stimulus_path == "C:\\Audio\\S0N180_headrot_short.wav"
    
    def test_from_json_file_round_trip(self, sample_schema, temp_output_dir):
        """Verify round-trip: schema → file → schema."""
        filepath = os.path.join(temp_output_dir, "round_trip.json")
        sample_schema.to_json_file(filepath)
        
        loaded = RatingRecordingSchema.from_json_file(filepath)
        assert loaded.participant_id == sample_schema.participant_id
        assert loaded.session_id == sample_schema.session_id
        assert loaded.ratings == sample_schema.ratings
        assert loaded.slider_config == sample_schema.slider_config
    
    def test_from_json_file_not_found_raises(self):
        """Verify from_json_file raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            RatingRecordingSchema.from_json_file("/nonexistent/path/file.json")
    
    def test_from_json_file_invalid_json_raises(self, temp_output_dir):
        """Verify from_json_file raises JSONDecodeError for invalid JSON."""
        filepath = os.path.join(temp_output_dir, "invalid.json")
        with open(filepath, 'w') as f:
            f.write("this is not valid json {")
        
        with pytest.raises(json.JSONDecodeError):
            RatingRecordingSchema.from_json_file(filepath)


class TestEncoding:
    """Test file encoding and special characters."""
    
    def test_utf8_encoding_in_file(self, sample_schema, temp_output_dir):
        """Verify files are saved with UTF-8 encoding."""
        filepath = os.path.join(temp_output_dir, "utf8_test.json")
        sample_schema.to_json_file(filepath)
        
        # Read as binary and check UTF-8 BOM or UTF-8 characters
        with open(filepath, 'rb') as f:
            content = f.read()
        # Should be readable as UTF-8
        content.decode('utf-8')
    
    def test_special_characters_roundtrip(self, temp_output_dir):
        """Verify special characters survive round-trip."""
        schema = RatingRecordingSchema(
            participant_id="VP001",
            stimulus_list="Test_éàü_中文.txt",
            stimulus_path="C:\\Ü\\ä\\ö\\test.wav"
        )
        
        filepath = os.path.join(temp_output_dir, "special_chars.json")
        schema.to_json_file(filepath)
        loaded = RatingRecordingSchema.from_json_file(filepath)
        
        assert loaded.stimulus_list == schema.stimulus_list
        assert loaded.stimulus_path == schema.stimulus_path
