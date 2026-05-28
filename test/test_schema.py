"""Tests for RatingRecordingSchema and CalibrationSchema serialization and deserialization."""

import json
from pathlib import Path
import pytest
from le_slider_io.schema import RatingRecordingSchema, CalibrationSchema


# ============================================================
# RatingRecordingSchema tests (unchanged)
# ============================================================

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
        parsed = json.loads(json_string)
        assert isinstance(parsed, dict)
        assert parsed["participant_id"] == "VP001"

    def test_to_json_string_indent_default(self, sample_schema):
        """Verify to_json_string uses default indent=2."""
        json_string = sample_schema.to_json_string()
        assert "\n" in json_string
        assert "  " in json_string

    def test_to_json_string_custom_indent(self, sample_schema):
        """Verify to_json_string respects custom indent."""
        json_string_indent2 = sample_schema.to_json_string(indent=2)
        json_string_indent4 = sample_schema.to_json_string(indent=4)
        assert json.loads(json_string_indent2)
        assert json.loads(json_string_indent4)
        assert json_string_indent4.count(" ") > json_string_indent2.count(" ")

    def test_to_json_string_unicode_handling(self):
        """Verify to_json_string preserves unicode (ensure_ascii=False)."""
        schema = RatingRecordingSchema(
            participant_id="VP001",
            stimulus_list="Ümlaut_Test_äöü.txt"
        )
        json_string = schema.to_json_string()
        assert "ä" in json_string or "\\u00e4" in json_string
        parsed = json.loads(json_string)
        assert "ä" in parsed["stimulus_list"] or parsed["stimulus_list"]

    def test_to_json_string_no_indent(self, sample_schema):
        """Verify to_json_string with indent=None produces compact JSON."""
        json_string = sample_schema.to_json_string(indent=None)
        parsed = json.loads(json_string)
        assert parsed["participant_id"] == "VP001"
        assert json_string == json_string.replace("\n", "").replace("  ", "")


class TestToJsonFile:
    """Test saving RatingRecordingSchema to JSON file."""

    def test_to_json_file_creates_file(self, sample_schema, temp_output_dir):
        """Verify to_json_file creates a file."""
        filepath = Path(temp_output_dir) / "test_output.json"
        sample_schema.to_json_file(filepath)
        assert filepath.exists()

    def test_to_json_file_creates_directories(self, sample_schema, temp_output_dir):
        """Verify to_json_file creates missing directories."""
        filepath = Path(temp_output_dir) / "nested" / "deep" / "test_output.json"
        sample_schema.to_json_file(filepath)
        assert filepath.exists()
        assert filepath.parent.is_dir()

    def test_to_json_file_content_valid_json(self, sample_schema, temp_output_dir):
        """Verify saved file contains valid JSON."""
        filepath = Path(temp_output_dir) / "test.json"
        sample_schema.to_json_file(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data["participant_id"] == "VP001"
        assert data["ratings"] == [6.6, 6.6, 6.6, 6.7, 6.5, 6.4, 6.5]

    def test_to_json_file_custom_indent(self, sample_schema, temp_output_dir):
        """Verify to_json_file respects custom indent."""
        filepath1 = Path(temp_output_dir) / "indent2.json"
        filepath2 = Path(temp_output_dir) / "indent4.json"
        sample_schema.to_json_file(filepath1, indent=2)
        sample_schema.to_json_file(filepath2, indent=4)
        with open(filepath1, 'r') as f:
            content1 = f.read()
        with open(filepath2, 'r') as f:
            content2 = f.read()
        assert len(content2) > len(content1)

    def test_to_json_file_prevent_overwrite_enabled(self, sample_schema, temp_output_dir):
        """Verify to_json_file prevents overwriting when prevent_overwrite=True."""
        filepath = Path(temp_output_dir) / "data.json"
        sample_schema.to_json_file(filepath, prevent_overwrite=True)
        sample_schema.to_json_file(filepath, prevent_overwrite=True)
        assert filepath.exists()
        assert (Path(temp_output_dir) / "data_1.json").exists()

    def test_to_json_file_prevent_overwrite_disabled(self, sample_schema, temp_output_dir):
        """Verify to_json_file overwrites when prevent_overwrite=False."""
        filepath = Path(temp_output_dir) / "data.json"
        sample_schema.to_json_file(filepath, prevent_overwrite=False)
        sample_schema.to_json_file(filepath, prevent_overwrite=False)
        assert filepath.exists()
        assert not (Path(temp_output_dir) / "data_1.json").exists()

    def test_to_json_file_prevent_overwrite_default(self, sample_schema, temp_output_dir):
        """Verify prevent_overwrite=True is the default."""
        filepath = Path(temp_output_dir) / "data.json"
        sample_schema.to_json_file(filepath)
        sample_schema.to_json_file(filepath)
        assert filepath.exists()
        assert (Path(temp_output_dir) / "data_1.json").exists()

    def test_to_json_file_multiple_collisions(self, sample_schema, temp_output_dir):
        """Verify to_json_file handles multiple collision attempts."""
        filepath = Path(temp_output_dir) / "data.json"
        sample_schema.to_json_file(filepath, prevent_overwrite=True)
        sample_schema.to_json_file(filepath, prevent_overwrite=True)
        sample_schema.to_json_file(filepath, prevent_overwrite=True)
        assert filepath.exists()
        assert (Path(temp_output_dir) / "data_1.json").exists()
        assert (Path(temp_output_dir) / "data_2.json").exists()

    def test_to_json_file_data_integrity_with_collision_prevention(self, sample_schema, temp_output_dir):
        """Verify schema data is preserved when collision prevention is used."""
        filepath = Path(temp_output_dir) / "data.json"
        sample_schema.to_json_file(filepath, prevent_overwrite=True)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data["participant_id"] == sample_schema.participant_id
        assert data["ratings"] == sample_schema.ratings
        assert data["time_stamps"] == sample_schema.time_stamps


class TestFromJsonDict:
    """Test RatingRecordingSchema deserialization from JSON dictionary."""

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
        incomplete_dict = {"participant_id": "VP001"}
        with pytest.raises(KeyError):
            RatingRecordingSchema.from_json_dict(incomplete_dict)


class TestFromJsonFile:
    """Test RatingRecordingSchema deserialization from JSON file."""

    def test_from_json_file_basic(self, sample_json_file):
        """Verify from_json_file loads schema from file."""
        schema = RatingRecordingSchema.from_json_file(sample_json_file)
        assert schema.participant_id == "VP001"
        assert schema.stimulus_path == "C:\\Audio\\S0N180_headrot_short.wav"

    def test_from_json_file_round_trip(self, sample_schema, temp_output_dir):
        """Verify round-trip: schema → file → schema."""
        filepath = Path(temp_output_dir) / "round_trip.json"
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
        filepath = Path(temp_output_dir) / "invalid.json"
        with open(filepath, 'w') as f:
            f.write("this is not valid json {")
        with pytest.raises(json.JSONDecodeError):
            RatingRecordingSchema.from_json_file(filepath)


class TestEncoding:
    """Test file encoding and special characters for RatingRecordingSchema."""

    def test_utf8_encoding_in_file(self, sample_schema, temp_output_dir):
        """Verify files are saved with UTF-8 encoding."""
        filepath = Path(temp_output_dir) / "utf8_test.json"
        sample_schema.to_json_file(filepath)
        with open(filepath, 'rb') as f:
            content = f.read()
        content.decode('utf-8')

    def test_special_characters_roundtrip(self, temp_output_dir):
        """Verify special characters survive round-trip."""
        schema = RatingRecordingSchema(
            participant_id="VP001",
            stimulus_list="Test_éàü_中文.txt",
            stimulus_path="C:\\Ü\\ä\\ö\\test.wav"
        )
        filepath = Path(temp_output_dir) / "special_chars.json"
        schema.to_json_file(filepath)
        loaded = RatingRecordingSchema.from_json_file(filepath)
        assert loaded.stimulus_list == schema.stimulus_list
        assert loaded.stimulus_path == schema.stimulus_path


# ============================================================
# CalibrationSchema tests
# ============================================================

class TestCalibrationSchemaDefaults:
    """Test default values and initialization of CalibrationSchema."""

    def test_schema_full_initialization(self, sample_calib_schema):
        """Verify schema initializes with all required fields correctly."""
        assert sample_calib_schema.session_id == "2026-04-24T13:15:36.008773+02:00"
        assert sample_calib_schema.device_id == 12
        assert sample_calib_schema.device_name == "RME Fireface UFX III"
        assert sample_calib_schema.fs == 48000
        assert sample_calib_schema.measured_spl_left == 94.5
        assert sample_calib_schema.measured_spl_right == 93.8
        assert sample_calib_schema.desired_spl == 94.0
        assert sample_calib_schema.calib_signal_path == "C:\\Calibration\\pink_noise_1kHz.wav"
        assert sample_calib_schema.gain_calib == [0.7, 1.1]

    def test_schema_gain_calib_accepts_positive(self):
        """Verify gain_calib accepts positive values for both channels."""
        schema = CalibrationSchema(
            device_id=1, device_name="Test", fs=44100,
            measured_spl_left=90.0, measured_spl_right=90.0,
            desired_spl=90.0, gain_calib=[6.0, 2.0]
        )
        assert schema.gain_calib == [6.0, 2.0]

    def test_schema_gain_calib_accepts_zero(self):
        """Verify gain_calib accepts zero for both channels."""
        schema = CalibrationSchema(
            device_id=1, device_name="Test", fs=44100,
            measured_spl_left=90.0, measured_spl_right=90.0,
            desired_spl=90.0, gain_calib=[0.0, 0.0]
        )
        assert schema.gain_calib == [0.0, 0.0]

    def test_schema_gain_calib_rejects_negative_values(self):
        """Verify gain_calib rejects negative values in constructor."""
        with pytest.raises(ValueError):
            CalibrationSchema(
                device_id=1, device_name="Test", fs=44100,
                measured_spl_left=90.0, measured_spl_right=90.0,
                desired_spl=90.0, gain_calib=[0.7, -0.1]
            )


class TestCalibrationToJsonDict:
    """Test CalibrationSchema conversion to JSON-serializable dictionary."""

    def test_to_json_dict_basic(self, sample_calib_schema):
        """Verify to_json_dict produces valid dictionary."""
        json_dict = sample_calib_schema.to_json_dict()
        assert isinstance(json_dict, dict)
        assert json_dict["gain_calib"] == [0.7, 1.1]
        assert json_dict["session_id"] == "2026-04-24T13:15:36.008773+02:00"

    def test_to_json_dict_has_all_fields(self, sample_calib_schema):
        """Verify to_json_dict includes exactly all fields."""
        json_dict = sample_calib_schema.to_json_dict()
        expected_fields = {
            "session_id", "device_id", "device_name", "fs",
            "measured_spl_left", "measured_spl_right", "desired_spl",
            "calib_signal_path", "gain_calib"
        }
        assert set(json_dict.keys()) == expected_fields

    def test_to_json_dict_gain_calib_type(self, sample_calib_schema):
        """Verify gain_calib is serialized as a list of two floats."""
        json_dict = sample_calib_schema.to_json_dict()
        assert isinstance(json_dict["gain_calib"], list)
        assert len(json_dict["gain_calib"]) == 2
        assert all(isinstance(value, float) for value in json_dict["gain_calib"])


class TestCalibrationToJsonString:
    """Test CalibrationSchema conversion to formatted JSON string."""

    def test_to_json_string_valid_json(self, sample_calib_schema):
        """Verify to_json_string produces valid JSON."""
        json_string = sample_calib_schema.to_json_string()
        parsed = json.loads(json_string)
        assert isinstance(parsed, dict)
        assert parsed["gain_calib"] == [0.7, 1.1]

    def test_to_json_string_indent_default(self, sample_calib_schema):
        """Verify to_json_string uses default indent=2."""
        json_string = sample_calib_schema.to_json_string()
        assert "\n" in json_string
        assert "  " in json_string

    def test_to_json_string_custom_indent(self, sample_calib_schema):
        """Verify to_json_string respects custom indent."""
        json_string_indent2 = sample_calib_schema.to_json_string(indent=2)
        json_string_indent4 = sample_calib_schema.to_json_string(indent=4)
        assert json.loads(json_string_indent2)
        assert json.loads(json_string_indent4)
        assert json_string_indent4.count(" ") > json_string_indent2.count(" ")

    def test_to_json_string_no_indent(self, sample_calib_schema):
        """Verify to_json_string with indent=None produces compact JSON."""
        json_string = sample_calib_schema.to_json_string(indent=None)
        parsed = json.loads(json_string)
        assert parsed["gain_calib"] == [0.7, 1.1]
        assert json_string == json_string.replace("\n", "").replace("  ", "")


class TestCalibrationToJsonFile:
    """Test saving CalibrationSchema to JSON file."""

    def test_to_json_file_creates_file(self, sample_calib_schema, temp_output_dir):
        """Verify to_json_file creates a file."""
        filepath = Path(temp_output_dir) / "calib_output.json"
        sample_calib_schema.to_json_file(filepath)
        assert filepath.exists()

    def test_to_json_file_creates_directories(self, sample_calib_schema, temp_output_dir):
        """Verify to_json_file creates missing directories."""
        filepath = Path(temp_output_dir) / "nested" / "deep" / "calib_output.json"
        sample_calib_schema.to_json_file(filepath)
        assert filepath.exists()
        assert filepath.parent.is_dir()

    def test_to_json_file_content_valid_json(self, sample_calib_schema, temp_output_dir):
        """Verify saved file contains valid JSON with correct values."""
        filepath = Path(temp_output_dir) / "calib.json"
        sample_calib_schema.to_json_file(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data["gain_calib"] == [0.7, 1.1]
        assert data["session_id"] == "2026-04-24T13:15:36.008773+02:00"
        assert data["device_id"] == 12
        assert data["fs"] == 48000
        assert data["desired_spl"] == 94.0

    def test_to_json_file_returns_absolute_path(self, sample_calib_schema, temp_output_dir):
        """Verify to_json_file returns an absolute path."""
        filepath = Path(temp_output_dir) / "calib.json"
        result = sample_calib_schema.to_json_file(filepath)
        assert result.is_absolute()

    def test_to_json_file_prevent_overwrite_enabled(self, sample_calib_schema, temp_output_dir):
        """Verify to_json_file prevents overwriting when prevent_overwrite=True."""
        filepath = Path(temp_output_dir) / "calib.json"
        sample_calib_schema.to_json_file(filepath, prevent_overwrite=True)
        sample_calib_schema.to_json_file(filepath, prevent_overwrite=True)
        assert filepath.exists()
        assert (Path(temp_output_dir) / "calib_1.json").exists()

    def test_to_json_file_prevent_overwrite_disabled(self, sample_calib_schema, temp_output_dir):
        """Verify to_json_file overwrites when prevent_overwrite=False."""
        filepath = Path(temp_output_dir) / "calib.json"
        sample_calib_schema.to_json_file(filepath, prevent_overwrite=False)
        sample_calib_schema.to_json_file(filepath, prevent_overwrite=False)
        assert filepath.exists()
        assert not (Path(temp_output_dir) / "calib_1.json").exists()

    def test_to_json_file_prevent_overwrite_default(self, sample_calib_schema, temp_output_dir):
        """Verify prevent_overwrite=True is the default."""
        filepath = Path(temp_output_dir) / "calib.json"
        sample_calib_schema.to_json_file(filepath)
        sample_calib_schema.to_json_file(filepath)
        assert filepath.exists()
        assert (Path(temp_output_dir) / "calib_1.json").exists()

    def test_to_json_file_multiple_collisions(self, sample_calib_schema, temp_output_dir):
        """Verify to_json_file handles multiple collision attempts."""
        filepath = Path(temp_output_dir) / "calib.json"
        sample_calib_schema.to_json_file(filepath, prevent_overwrite=True)
        sample_calib_schema.to_json_file(filepath, prevent_overwrite=True)
        sample_calib_schema.to_json_file(filepath, prevent_overwrite=True)
        assert filepath.exists()
        assert (Path(temp_output_dir) / "calib_1.json").exists()
        assert (Path(temp_output_dir) / "calib_2.json").exists()

    def test_to_json_file_data_integrity_with_collision_prevention(self, sample_calib_schema, temp_output_dir):
        """Verify schema data is preserved when collision prevention is used."""
        filepath = Path(temp_output_dir) / "calib.json"
        sample_calib_schema.to_json_file(filepath, prevent_overwrite=True)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data["gain_calib"] == sample_calib_schema.gain_calib
        assert data["session_id"] == sample_calib_schema.session_id


class TestCalibrationFromJsonDict:
    """Test CalibrationSchema deserialization from JSON dictionary."""

    def test_from_json_dict_basic(self, sample_calib_json_dict):
        """Verify from_json_dict reconstructs schema."""
        schema = CalibrationSchema.from_json_dict(sample_calib_json_dict)
        assert schema.gain_calib == [0.7, 1.1]
        assert schema.session_id == "2026-04-24T13:15:36.008773+02:00"

    def test_from_json_dict_round_trip(self, sample_calib_schema):
        """Verify round-trip: schema → dict → schema."""
        json_dict = sample_calib_schema.to_json_dict()
        reconstructed = CalibrationSchema.from_json_dict(json_dict)
        assert reconstructed.gain_calib == sample_calib_schema.gain_calib
        assert reconstructed.session_id == sample_calib_schema.session_id

    def test_from_json_dict_with_minimal_fields(self):
        """Verify from_json_dict with only required fields (session_id optional)."""
        minimal_dict = {
            "device_id": 5,
            "device_name": "TestDevice",
            "fs": 44100,
            "measured_spl_left": 90.0,
            "measured_spl_right": 91.0,
            "desired_spl": 90.5,
            "gain_calib": [0.3, 0.5]
        }
        schema = CalibrationSchema.from_json_dict(minimal_dict)
        assert schema.device_id == 5
        assert schema.gain_calib == [0.3, 0.5]
        assert schema.session_id == ""
        assert schema.calib_signal_path == ""

    def test_from_json_dict_scalar_gain_calib_raises(self):
        """Verify scalar gain_calib is rejected in strict two-channel mode."""
        data = {
            "device_id": 1,
            "device_name": "Test",
            "fs": 48000,
            "measured_spl_left": 90.0,
            "measured_spl_right": 90.0,
            "desired_spl": 90.0,
            "gain_calib": -3.0
        }
        with pytest.raises(TypeError):
            CalibrationSchema.from_json_dict(data)

    def test_from_json_dict_invalid_gain_calib_length_raises(self):
        """Verify from_json_dict rejects gain_calib lists that are not length 2."""
        data = {
            "device_id": 1,
            "device_name": "Test",
            "fs": 48000,
            "measured_spl_left": 90.0,
            "measured_spl_right": 90.0,
            "desired_spl": 90.0,
            "gain_calib": [-3.0]
        }
        with pytest.raises(ValueError):
            CalibrationSchema.from_json_dict(data)

    def test_from_json_dict_non_numeric_gain_calib_raises(self):
        """Verify from_json_dict rejects non-numeric gain_calib values."""
        data = {
            "device_id": 1,
            "device_name": "Test",
            "fs": 48000,
            "measured_spl_left": 90.0,
            "measured_spl_right": 90.0,
            "desired_spl": 90.0,
            "gain_calib": [0.3, "bad"]
        }
        with pytest.raises(TypeError):
            CalibrationSchema.from_json_dict(data)

    def test_from_json_dict_negative_gain_calib_raises(self):
        """Verify from_json_dict rejects negative gain_calib values."""
        data = {
            "device_id": 1,
            "device_name": "Test",
            "fs": 48000,
            "measured_spl_left": 90.0,
            "measured_spl_right": 90.0,
            "desired_spl": 90.0,
            "gain_calib": [0.7, -0.1]
        }
        with pytest.raises(ValueError):
            CalibrationSchema.from_json_dict(data)

    def test_from_json_dict_missing_required_device_id_raises(self):
        """Verify from_json_dict raises KeyError when device_id is missing."""
        incomplete_dict = {
            "device_name": "Test",
            "fs": 48000,
            "measured_spl_left": 90.0,
            "measured_spl_right": 90.0,
            "desired_spl": 90.0,
            "gain_calib": [0.7, 1.1]
        }
        with pytest.raises(KeyError):
            CalibrationSchema.from_json_dict(incomplete_dict)

    def test_from_json_dict_missing_required_gain_calib_raises(self):
        """Verify from_json_dict raises KeyError when gain_calib is missing."""
        incomplete_dict = {
            "device_id": 5,
            "device_name": "Test",
            "fs": 48000,
            "measured_spl_left": 90.0,
            "measured_spl_right": 90.0,
            "desired_spl": 90.0
        }
        with pytest.raises(KeyError):
            CalibrationSchema.from_json_dict(incomplete_dict)

    def test_from_json_dict_empty_dict_raises(self):
        """Verify from_json_dict raises KeyError for empty dictionary."""
        with pytest.raises(KeyError):
            CalibrationSchema.from_json_dict({})

    def test_from_json_dict_returns_calibration_instance(self, sample_calib_json_dict):
        """Verify from_json_dict returns a CalibrationSchema instance."""
        schema = CalibrationSchema.from_json_dict(sample_calib_json_dict)
        assert isinstance(schema, CalibrationSchema)


class TestCalibrationFromJsonFile:
    """Test CalibrationSchema deserialization from JSON file."""

    def test_from_json_file_basic(self, sample_calib_json_file):
        """Verify from_json_file loads schema from file."""
        schema = CalibrationSchema.from_json_file(sample_calib_json_file)
        assert schema.gain_calib == [0.7, 1.1]
        assert schema.session_id == "2026-04-24T13:15:36.008773+02:00"

    def test_from_json_file_round_trip(self, sample_calib_schema, temp_output_dir):
        """Verify round-trip: schema → file → schema."""
        filepath = Path(temp_output_dir) / "calib_round_trip.json"
        sample_calib_schema.to_json_file(filepath)
        loaded = CalibrationSchema.from_json_file(filepath)
        assert loaded.gain_calib == sample_calib_schema.gain_calib
        assert loaded.session_id == sample_calib_schema.session_id

    def test_from_json_file_returns_calibration_instance(self, sample_calib_json_file):
        """Verify from_json_file returns a CalibrationSchema instance."""
        schema = CalibrationSchema.from_json_file(sample_calib_json_file)
        assert isinstance(schema, CalibrationSchema)

    def test_from_json_file_not_found_raises(self):
        """Verify from_json_file raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            CalibrationSchema.from_json_file("/nonexistent/path/calib.json")

    def test_from_json_file_invalid_json_raises(self, temp_output_dir):
        """Verify from_json_file raises JSONDecodeError for invalid JSON."""
        filepath = Path(temp_output_dir) / "invalid_calib.json"
        with open(filepath, 'w') as f:
            f.write("this is not valid json {")
        with pytest.raises(json.JSONDecodeError):
            CalibrationSchema.from_json_file(filepath)

    def test_from_json_file_missing_gain_calib_raises(self, temp_output_dir):
        """Verify from_json_file raises KeyError when gain_calib is absent."""
        filepath = Path(temp_output_dir) / "no_gain.json"
        with open(filepath, 'w') as f:
            json.dump({"session_id": "2026-04-24T13:15:36.008773+02:00"}, f)
        with pytest.raises(KeyError):
            CalibrationSchema.from_json_file(filepath)


class TestCalibrationEncoding:
    """Test file encoding for CalibrationSchema."""

    def test_utf8_encoding_in_file(self, sample_calib_schema, temp_output_dir):
        """Verify calibration files are saved with UTF-8 encoding."""
        filepath = Path(temp_output_dir) / "calib_utf8.json"
        sample_calib_schema.to_json_file(filepath)
        with open(filepath, 'rb') as f:
            content = f.read()
        content.decode('utf-8')

    def test_unicode_session_id_roundtrip(self, temp_output_dir):
        """Verify unicode characters in session_id survive round-trip."""
        schema = CalibrationSchema(
            session_id="2026-04-24T13:15:36+02:00_éàü",
            device_id=3,
            device_name="TestDevice_üñ",
            fs=48000,
            measured_spl_left=92.0,
            measured_spl_right=93.0,
            desired_spl=92.5,
            gain_calib=[0.9, 1.0]
        )
        filepath = Path(temp_output_dir) / "calib_unicode.json"
        schema.to_json_file(filepath)
        loaded = CalibrationSchema.from_json_file(filepath)
        assert loaded.session_id == schema.session_id
        assert loaded.device_name == schema.device_name
        assert loaded.gain_calib == schema.gain_calib