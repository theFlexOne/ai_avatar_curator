import json
from pathlib import Path
from datetime import datetime

from src.schemas import ProjectState

class StorageManager:
    """Manages serialization and deserialization of the ProjectState."""

    def __init__(self, metadata_path: str):
        self.metadata_path = Path(metadata_path)
        # Ensure the directory exists
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
    def load_state(self, subject_name: str) -> ProjectState:
        """Loads state from disk, or creates a new one if it doesn't exist."""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return ProjectState(**data)
        return ProjectState(subject_name=subject_name)
        
    def save_state(self, state: ProjectState) -> None:
        """Saves the state to disk, updating the 'updated_at' timestamp."""
        state.updated_at = datetime.utcnow()
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            f.write(state.model_dump_json(indent=2))
