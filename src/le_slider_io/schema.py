from dataclasses import dataclass, asdict, field
import json
from pathlib import Path
from typing import Dict, Any


@dataclass
class BaseSchema:
    """Base schema with shared JSON serialization logic."""

    def to_json_dict(self) -> Dict[str, Any]:
        """Convert schema to JSON-serializable dictionary."""
        return asdict(self)

    def to_json_string(self, indent: int = 2) -> str:
        """Convert schema to formatted JSON string."""
        return json.dumps(self.to_json_dict(), indent=indent, ensure_ascii=False)

    def to_json_file(self, filepath: str | Path, indent: int = 2, prevent_overwrite: bool = True) -> Path:
        """Save schema to JSON file.

        Args:
            filepath: Path to output JSON file
            indent: JSON indentation level
            prevent_overwrite: If True, appends numeric suffix to avoid overwriting

        Returns:
            Absolute path to the file that was written
        """
        from .recording import get_safe_filepath

        if prevent_overwrite:
            filepath = get_safe_filepath(filepath)

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json_string(indent=indent))

        return filepath.resolve()

    @classmethod
    def from_json_dict(cls, data: Dict[str, Any]) -> 'BaseSchema':
        """Create instance from dictionary. Must be implemented by subclasses."""
        raise NotImplementedError(f"{cls.__name__} must implement from_json_dict()")

    @classmethod
    def from_json_file(cls, filepath: str | Path) -> 'BaseSchema':
        """Load schema from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Schema instance of the calling class
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_json_dict(data)


@dataclass
class RatingRecordingSchema(BaseSchema):
    session_id: str = ""
    participant_id: str = ""
    stimulus_path: str = ""
    stimulus_list: str = ""
    stimulus_start: str = ""
    stimulus_end: str = ""
    slider_config: Dict[str, Any] = field(default_factory=dict)
    ratings: list = field(default_factory=list)
    time_stamps: list = field(default_factory=list)

    @classmethod
    def from_json_dict(cls, data: Dict[str, Any]) -> 'RatingRecordingSchema':
        return cls(
            participant_id=data['participant_id'],
            session_id=data.get('session_id', ''),
            stimulus_path=data['stimulus_path'],
            stimulus_list=data['stimulus_list'],
            stimulus_start=data.get('stimulus_start', ''),
            stimulus_end=data.get('stimulus_end', ''),
            slider_config=data.get('slider_config', {}),
            ratings=data.get('ratings', []),
            time_stamps=data.get('time_stamps', []),
        )


@dataclass
class CalibrationSchema(BaseSchema):
    session_id: str = ""
    gain_calib: float = 0.0

    @classmethod
    def from_json_dict(cls, data: Dict[str, Any]) -> 'CalibrationSchema':
        return cls(
            session_id=data.get('session_id', ''),
            gain_calib=data['gain_calib'],
        )