from typing import List, Optional, Tuple, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ImageSource(str, Enum):
    GOOGLE = "google"
    YANDEX = "yandex"
    BING = "bing"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    LOCAL = "local"
    OTHER = "other"

class ProcessingStatus(str, Enum):
    RAW = "raw"
    FILTERED_PASS = "filtered_pass"
    FILTERED_FAIL = "filtered_fail"
    FACE_PASS = "face_pass"
    FACE_FAIL = "face_fail"
    ID_PASS = "id_pass"
    ID_FAIL = "id_fail"
    INTERIM = "interim"
    PROCESSED = "processed"
    REJECTED = "rejected"

class Pose(BaseModel):
    """Estimated head pose angles."""
    yaw: float
    pitch: float
    roll: float

class FaceMetrics(BaseModel):
    """Metrics related to the detected face in an image."""
    bounding_box: Tuple[int, int, int, int] = Field(..., description="Top, Right, Bottom, Left coordinates")
    face_size: int = Field(..., description="Size of the bounding box (width or max dimension)")
    sharpness_score: float = Field(..., description="Laplacian variance score indicating blurriness")
    similarity_score: Optional[float] = Field(None, description="Cosine similarity score against reference embedding")
    pose: Optional[Pose] = Field(None, description="Estimated head pose")
    landmarks: Optional[dict[str, List[Tuple[int, int]]]] = Field(None, description="Facial landmarks (eyes, nose, mouth)")
    has_occlusions: Optional[bool] = Field(None, description="Whether eyes/mouth are significantly occluded")
    
class ScrapedImageResult(BaseModel):
    """Raw result returned from a scraper before downloading."""
    image_url: str = Field(..., description="Direct URL to the image")
    source: Union[ImageSource, str] = Field(..., description="Source engine or platform")
    page_url: Optional[str] = Field(None, description="URL of the webpage containing the image")
    title: Optional[str] = Field(None, description="Title, alt text, or snippet from the search result")
    search_query: Optional[str] = Field(None, description="The query string used to find this image")
    expected_width: Optional[int] = None
    expected_height: Optional[int] = None

class ImageMetadata(BaseModel):
    """Data structure representing a scraped image and its metadata after download."""
    image_hash: str = Field(..., description="MD5 or SHA-256 hash for deduplication")
    source_url: str
    page_url: Optional[str] = Field(None, description="URL of the webpage where the image was found")
    source: Union[ImageSource, str]
    search_query: Optional[str] = Field(None, description="The query string used to find this image")
    title: Optional[str] = Field(None, description="Title or alt text of the image")
    original_filename: str
    original_width: Optional[int] = None
    original_height: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    local_path: Optional[str] = Field(None, description="Local path in data/raw or data/interim")
    status: ProcessingStatus = Field(default=ProcessingStatus.RAW)
    face_metrics: Optional[FaceMetrics] = None
    error_message: Optional[str] = Field(None, description="Reason if the status is REJECTED")
    
class CuratedAvatar(BaseModel):
    """A processed and curated avatar ready for dataset use."""
    metadata: ImageMetadata
    face_metrics: FaceMetrics
    cropped_file_path: str = Field(..., description="Local path to the cropped image in data/processed")
    is_approved: bool = Field(False, description="Manual verification status")
    tags: List[str] = Field(default_factory=list, description="Descriptive tags (e.g., 'professional', 'casual')")
    caption: Optional[str] = Field(None, description="Auto-generated or manual caption for training (e.g., Dreambooth/Flux)")

class ProjectState(BaseModel):
    """Overall state of a curation project, easily serialized to metadata.json."""
    subject_name: str = Field(..., description="Name of the person being curated")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    images: dict[str, ImageMetadata] = Field(default_factory=dict, description="Dictionary of image_hash -> ImageMetadata")
    avatars: dict[str, CuratedAvatar] = Field(default_factory=dict, description="Dictionary of image_hash -> CuratedAvatar")
    
class SearchConfig(BaseModel):
    """Configuration for search operations."""
    query: str
    engines: List[str] = Field(default_factory=lambda: ["google", "yandex", "bing"])
    max_results: int = Field(default=10)
    offset: int = Field(default=0, description="Pagination offset (e.g., page index or result count)")
    reference_images: List[str] = Field(default_factory=list, description="Paths to reference images for reverse search/embeddings")
