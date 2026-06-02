import logging
from pathlib import Path
import cv2
import numpy as np
from typing import Tuple

from src.schemas import ImageMetadata

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handles image manipulation tasks like cropping, resizing, and normalization."""

    def __init__(self, output_dir: str, target_size: int = 512, crop_scale: float = 1.5):
        """
        Args:
            output_dir: Directory to save processed images.
            target_size: The target resolution for the final square image (e.g., 512).
            crop_scale: Multiplier to determine the crop area around the face bbox. 
                        1.0 is a tight crop, 2.0 is a loose crop.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.target_size = target_size
        self.crop_scale = crop_scale
        logger.info(f"Initialized ImageProcessor with output_dir='{output_dir}', target_size={target_size}")

    def process_image(self, metadata: ImageMetadata) -> str:
        """
        Crops, resizes, and saves the final processed image.

        Args:
            metadata: The metadata of the image to process, including face_metrics.

        Returns:
            The path to the newly created processed image.
        """
        if not metadata.local_path or not Path(metadata.local_path).exists():
            raise FileNotFoundError(f"Source image not found for processing: {metadata.local_path}")
            
        if not metadata.face_metrics:
            raise ValueError(f"No face metrics found for image {metadata.image_hash}")

        try:
            image = cv2.imread(metadata.local_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # Work in RGB

            # 1. Face Alignment
            if metadata.face_metrics.landmarks:
                image = self._align_face(image, metadata.face_metrics.landmarks)

            # 2. Smart Cropping
            cropped_image = self._smart_crop(image, metadata.face_metrics.bounding_box)

            # 3. Resizing
            resized_image = cv2.resize(cropped_image, (self.target_size, self.target_size), interpolation=cv2.INTER_AREA)

            # 4. Save to processed directory
            output_filename = f"{metadata.image_hash}.png" # Standardize to PNG
            output_path = self.output_dir / output_filename
            
            # Convert back to BGR for OpenCV to save correctly
            cv2.imwrite(str(output_path), cv2.cvtColor(resized_image, cv2.COLOR_RGB2BGR))

            logger.info(f"Successfully processed and saved image to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to process image {metadata.image_hash}: {e}")
            raise

    def _align_face(self, image: np.ndarray, landmarks: dict) -> np.ndarray:
        """
        Rotates the image so that the eyes are horizontal.
        """
        try:
            left_eye = landmarks.get("left_eye")
            right_eye = landmarks.get("right_eye")
            
            if not left_eye or not right_eye:
                return image
                
            # Get the center of each eye
            left_eye_center = np.mean(left_eye, axis=0).astype(int)
            right_eye_center = np.mean(right_eye, axis=0).astype(int)
            
            # Calculate the angle between the eyes
            dy = right_eye_center[1] - left_eye_center[1]
            dx = right_eye_center[0] - left_eye_center[0]
            angle = np.degrees(np.arctan2(dy, dx))
            
            # Rotate the image around the center between the eyes
            eye_center = ((left_eye_center[0] + right_eye_center[0]) // 2, 
                          (left_eye_center[1] + right_eye_center[1]) // 2)
            
            matrix = cv2.getRotationMatrix2D(eye_center, angle, 1.0)
            img_height, img_width, _ = image.shape
            rotated_image = cv2.warpAffine(image, matrix, (img_width, img_height), flags=cv2.INTER_CUBIC)
            
            return rotated_image
        except Exception as e:
            logger.warning(f"Failed to align face: {e}")
            return image

    def _smart_crop(self, image: np.ndarray, face_location: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Crops the image around the face location to a square aspect ratio.
        """
        top, right, bottom, left = face_location
        
        # Calculate center and size of the face bbox
        face_center_x = (left + right) // 2
        face_center_y = (top + bottom) // 2
        face_height = bottom - top
        face_width = right - left
        
        # Determine the size of the square crop area
        crop_size = int(max(face_height, face_width) * self.crop_scale)
        
        # Calculate the top-left corner of the crop area
        crop_left = max(0, face_center_x - crop_size // 2)
        crop_top = max(0, face_center_y - crop_size // 2)

        # Ensure the crop area does not exceed image boundaries
        img_height, img_width, _ = image.shape
        crop_right = min(img_width, crop_left + crop_size)
        crop_bottom = min(img_height, crop_top + crop_size)

        # Final crop
        cropped_image = image[crop_top:crop_bottom, crop_left:crop_right]

        return cropped_image
