from abc import ABC, abstractmethod
import logging
from typing import List, Optional
from src.context import ProjectContext
from src.schemas import ProcessingStatus, SearchConfig
from src.scrapers.manager import ScraperManager
from src.filters.basic_filters import BasicFilter
from src.filters.face_recognition_filters import FaceRecognitionFilter
from src.processors.image_processor import ImageProcessor
from src.schemas import CuratedAvatar

logger = logging.getLogger(__name__)

class PipelineStage(ABC):
    """
    Abstraction for a single step in the curation pipeline.
    Provides a Seam between orchestration and implementation.
    """
    @abstractmethod
    async def run(self, ctx: ProjectContext) -> int:
        """Executes the stage logic and returns the number of images handled."""
        pass

class ScrapeStage(PipelineStage):
    """Adapter for image acquisition using ScraperManager."""
    def __init__(self, manager: ScraperManager, config: SearchConfig):
        self.manager = manager
        self.config = config

    async def run(self, ctx: ProjectContext) -> int:
        before_count = len(ctx.images)
        await self.manager.run(self.config, ctx)
        return len(ctx.images) - before_count

class FilterStage(PipelineStage):
    """Adapter for the Audit Loop filtering process."""
    def __init__(self, config_data: dict, subject_name: str, reference_images: List[str] = None):
        self.config_data = config_data
        self.subject_name = subject_name
        self.reference_images = reference_images

    async def run(self, ctx: ProjectContext) -> int:
        images_to_process = ctx.get_images_by_status(ProcessingStatus.RAW)
        if not images_to_process:
            return 0

        filter_cfg = self.config_data.get("filtering", {})
        basic_filter = BasicFilter(
            min_resolution=filter_cfg.get("min_resolution", [512, 512])[0],
            sharpness_threshold=filter_cfg.get("sharpness_threshold", 100.0)
        )
        face_filter = FaceRecognitionFilter(
            subject_name=self.subject_name,
            reference_path=self.reference_images[0] if self.reference_images else None
        )

        success_count = 0
        for metadata in images_to_process:
            img_hash = metadata.image_hash
            if not basic_filter.apply_all(metadata):
                ctx.update_image_status(img_hash, ProcessingStatus.FILTERED_FAIL)
                continue
            
            ctx.update_image_status(img_hash, ProcessingStatus.FILTERED_PASS)
            metrics = await face_filter.analyze_face(metadata)
            
            if not metrics:
                ctx.update_image_status(img_hash, ProcessingStatus.FACE_FAIL)
                continue
            
            metadata.face_metrics = metrics
            ctx.update_image_status(img_hash, ProcessingStatus.FACE_PASS)

            if metrics.similarity_score is not None and metrics.similarity_score < 0.4:
                ctx.update_image_status(img_hash, ProcessingStatus.ID_FAIL)
                continue
            
            if metrics.has_occlusions:
                ctx.update_image_status(img_hash, ProcessingStatus.ID_FAIL)
                continue

            ctx.update_image_status(img_hash, ProcessingStatus.ID_PASS)
            success_count += 1
            
        return success_count

class AlignStage(PipelineStage):
    """Adapter for final image processing (alignment/cropping)."""
    def __init__(self, processor: ImageProcessor):
        self.processor = processor

    async def run(self, ctx: ProjectContext) -> int:
        images_to_process = ctx.get_images_by_status(ProcessingStatus.ID_PASS)
        if not images_to_process:
            return 0
            
        success_count = 0
        for metadata in images_to_process:
            try:
                processed_path = self.processor.process_image(metadata)
                avatar = CuratedAvatar(
                    metadata=metadata,
                    face_metrics=metadata.face_metrics,
                    cropped_file_path=processed_path
                )
                ctx.add_avatar(avatar)
                success_count += 1
            except Exception as e:
                ctx.update_image_status(metadata.image_hash, ProcessingStatus.REJECTED, error_message=str(e))
        
        return success_count
