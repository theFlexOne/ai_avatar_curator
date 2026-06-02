import json
import logging
from pathlib import Path
from datetime import datetime

from src.schemas import ProjectState

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages serialization and deserialization of the ProjectState."""

    def __init__(self, metadata_path: str):
        self.metadata_path = Path(metadata_path)
        # Ensure the directory exists
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
    def load_state(self, subject_name: str) -> ProjectState:
        """Loads state from disk, or creates a new one if it doesn't exist."""
        if self.metadata_path.exists():
            logger.debug(f"Loading state from: {self.metadata_path.resolve()}")
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                state = ProjectState(**data)
                logger.debug(f"Loaded {len(state.images)} image records.")
                return state
        
        logger.info(f"No existing metadata file found. Creating new state for subject: {subject_name}")
        return ProjectState(subject_name=subject_name)
        
    def save_state(self, state: ProjectState) -> None:
        """Saves the state to disk, updating the 'updated_at' timestamp."""
        state.updated_at = datetime.utcnow()
        logger.debug(f"Saving state with {len(state.images)} images to: {self.metadata_path.resolve()}")
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            f.write(state.model_dump_json(indent=2))
        logger.debug("State saved successfully.")
