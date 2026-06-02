import logging
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from src.schemas import ProjectState, ImageMetadata, ProcessingStatus, CuratedAvatar
from src.storage import StorageManager

logger = logging.getLogger(__name__)

class ProjectContext:
    """
    A deep module that provides leverage for managing a subject's curation project.
    
    It wraps the shallow ProjectState (data) and provides a high-level interface 
    for querying and transitioning state, ensuring locality for business rules.
    """

    def __init__(self, subject_name: str, metadata_path: str):
        self.storage = StorageManager(metadata_path)
        self.state: ProjectState = self.storage.load_state(subject_name)
        self._subject_name = subject_name

    @property
    def images(self) -> Dict[str, ImageMetadata]:
        return self.state.images

    @property
    def avatars(self) -> Dict[str, CuratedAvatar]:
        return self.state.avatars

    def get_images_by_status(self, status: ProcessingStatus) -> List[ImageMetadata]:
        """Leverage: Single call to find all work for a specific pipeline stage."""
        return [meta for meta in self.state.images.values() if meta.status == status]

    def update_image_status(
        self, 
        image_hash: str, 
        status: ProcessingStatus, 
        error_message: Optional[str] = None
    ) -> None:
        """Locality: Centralized logic for state transitions and error logging."""
        if image_hash not in self.state.images:
            raise ValueError(f"Image {image_hash} not found in project state.")
        
        metadata = self.state.images[image_hash]
        old_status = metadata.status
        metadata.status = status
        if error_message:
            metadata.error_message = error_message
        
        logger.debug(f"Transitioned {image_hash} from {old_status} to {status}")

    def add_image(self, metadata: ImageMetadata) -> bool:
        """Adds a new image if it doesn't already exist (deduplication)."""
        if metadata.image_hash in self.state.images:
            return False
        
        self.state.images[metadata.image_hash] = metadata
        return True
        
    def add_avatar(self, avatar: CuratedAvatar) -> None:
        """Ensures consistent state when a new curated avatar is produced."""
        self.state.avatars[avatar.metadata.image_hash] = avatar
        self.update_image_status(avatar.metadata.image_hash, ProcessingStatus.PROCESSED)

    def save(self) -> None:
        """Persists the current state to disk."""
        self.storage.save_state(self.state)
        logger.info(f"Project state for '{self._subject_name}' persisted.")
