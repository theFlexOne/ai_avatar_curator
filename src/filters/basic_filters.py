import cv2
from pathlib import Path
import logging

from src.schemas import ImageMetadata

logger = logging.getLogger(__name__)

class BasicFilter:
    """Encapsulates basic image filtering operations."""

    def __init__(
        self,
        min_resolution: int = 512,
        sharpness_threshold: float = 100.0,
        brightness_range: tuple[int, int] = (40, 240),
    ):
        self.min_resolution = min_resolution
        self.sharpness_threshold = sharpness_threshold
        self.brightness_range = brightness_range
        logger.info(
            f"Initialized BasicFilter: min_res={min_resolution}, "
            f"sharpness_th={sharpness_threshold}, brightness={brightness_range}"
        )

    def is_sharp(self, image_path: str) -> bool:
        """
        Checks if an image is sharp based on the variance of the Laplacian.
        """
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                logger.warning(f"Could not read image for sharpness check: {image_path}")
                return False
            
            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
            logger.debug(f"Image {Path(image_path).name} Laplacian variance: {laplacian_var:.2f}")
            return laplacian_var > self.sharpness_threshold
        except Exception as e:
            logger.error(f"Error checking sharpness for {image_path}: {e}")
            return False

    def is_high_resolution(self, image_path: str) -> bool:
        """
        Checks if an image meets the minimum resolution requirement.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.warning(f"Could not read image for resolution check: {image_path}")
                return False
            
            height, width, _ = image.shape
            logger.debug(f"Image {Path(image_path).name} resolution: {width}x{height}")
            return height >= self.min_resolution and width >= self.min_resolution
        except Exception as e:
            logger.error(f"Error checking resolution for {image_path}: {e}")
            return False

    def is_well_lit(self, image_path: str) -> bool:
        """
        Checks if an image is within an acceptable brightness range.
        """
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                logger.warning(f"Could not read image for brightness check: {image_path}")
                return False
            
            avg_brightness = cv2.mean(image)[0]
            logger.debug(f"Image {Path(image_path).name} average brightness: {avg_brightness:.2f}")
            
            min_b, max_b = self.brightness_range
            return min_b <= avg_brightness <= max_b
        except Exception as e:
            logger.error(f"Error checking brightness for {image_path}: {e}")
            return False

    def apply_all(self, metadata: ImageMetadata) -> bool:
        """
        Applies all basic filters to a given image.

        Returns:
            True if the image passes all filters, False otherwise.
        """
        if not metadata.local_path or not Path(metadata.local_path).exists():
            logger.warning(f"Image path not found for {metadata.image_hash}, skipping filters.")
            return False

        if not self.is_high_resolution(metadata.local_path):
            logger.info(f"Image {metadata.image_hash} failed resolution check.")
            return False
        
        if not self.is_well_lit(metadata.local_path):
            logger.info(f"Image {metadata.image_hash} failed brightness check.")
            return False
            
        if not self.is_sharp(metadata.local_path):
            logger.info(f"Image {metadata.image_hash} failed sharpness check.")
            return False
            
        logger.info(f"Image {metadata.image_hash} passed all basic filters.")
        return True
