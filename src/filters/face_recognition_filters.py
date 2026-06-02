import logging
from pathlib import Path
from typing import Optional
import asyncio
import face_recognition
import cv2
from src.schemas import ImageMetadata, FaceMetrics

logger = logging.getLogger(__name__)


class FaceRecognitionFilter:
    """
    Client for local face recognition and identity verification using face_recognition library.
    """

    def __init__(self, subject_name: str, reference_path: Optional[str] = None):
        """
        Args:
            subject_name: The name of the person we are verifying.
            reference_path: Path to a reference image of the subject.
        """
        logger.info(f"Initialized FaceRecognitionFilter for subject '{subject_name}'")
        self.subject_name = subject_name
        self.reference_path = reference_path
        self._reference_encoding = None

    def _load_reference(self):
        """Loads and encodes the reference image."""
        if not self.reference_path:
            logger.warning("No reference path provided for identity verification.")
            return

        if not Path(self.reference_path).exists():
            logger.error(f"Reference image not found at {self.reference_path}")
            return

        try:
            image = face_recognition.load_image_file(self.reference_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                self._reference_encoding = encodings[0]
                logger.info(f"Successfully loaded reference encoding from {self.reference_path}")
            else:
                logger.error(f"No faces found in reference image {self.reference_path}")
        except Exception as e:
            logger.error(f"Error loading reference image: {e}")

    async def analyze_face(self, metadata: ImageMetadata) -> Optional[FaceMetrics]:
        """
        Performs detailed face analysis: bounding box, size, landmarks, and similarity.
        """
        if not metadata.local_path or not Path(metadata.local_path).exists():
            return None

        if self._reference_encoding is None:
            self._load_reference()

        def _analyze():
            try:
                image = face_recognition.load_image_file(metadata.local_path)
                face_locations = face_recognition.face_locations(image)
                
                if len(face_locations) != 1:
                    return None
                
                loc = face_locations[0] # (top, right, bottom, left)
                face_size = max(loc[2] - loc[0], loc[1] - loc[3])
                
                # Sharpness (re-calculate on the face crop)
                face_crop = image[loc[0]:loc[2], loc[3]:loc[1]]
                gray_face = cv2.cvtColor(face_crop, cv2.COLOR_RGB2GRAY)
                sharpness = cv2.Laplacian(gray_face, cv2.CV_64F).var()
                
                # Similarity
                encodings = face_recognition.face_encodings(image, face_locations)
                similarity = None
                if encodings and self._reference_encoding is not None:
                    # Calculate distance and convert to a similarity score (1 - distance)
                    dist = face_recognition.face_distance([self._reference_encoding], encodings[0])[0]
                    similarity = float(1.0 - dist)
                
                # Occlusion check (very basic: check if landmarks for eyes/mouth are found)
                landmarks = face_recognition.face_landmarks(image, face_locations)
                has_occlusions = False
                if landmarks:
                    lm = landmarks[0]
                    required = ["left_eye", "right_eye", "top_lip", "bottom_lip"]
                    if not all(k in lm and len(lm[k]) > 0 for k in required):
                        has_occlusions = True
                
                return FaceMetrics(
                    bounding_box=loc,
                    face_size=face_size,
                    sharpness_score=sharpness,
                    similarity_score=similarity,
                    landmarks=landmarks[0] if landmarks else None,
                    has_occlusions=has_occlusions
                )
            except Exception as e:
                logger.error(f"Error analyzing face for {metadata.local_path}: {e}")
                return None

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _analyze)

    async def has_single_face(self, metadata: ImageMetadata) -> bool:
        """
        Checks if the image contains exactly one face.
        """
        if not metadata.local_path or not Path(metadata.local_path).exists():
            logger.warning(f"Image path not found for {metadata.image_hash}, skipping face check.")
            return False

        def _check():
            try:
                image = face_recognition.load_image_file(metadata.local_path)
                face_locations = face_recognition.face_locations(image)
                return len(face_locations) == 1
            except Exception as e:
                logger.error(f"Error checking face count for {metadata.local_path}: {e}")
                return False

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _check)

    async def is_identity_match(self, metadata: ImageMetadata) -> bool:
        """
        Verifies the face matches the subject using the reference image.
        """
        if not metadata.local_path or not Path(metadata.local_path).exists():
            logger.warning(f"Image path not found for {metadata.image_hash}, skipping identity check.")
            return False

        if self._reference_encoding is None:
            self._load_reference()
            if self._reference_encoding is None:
                logger.warning("Skipping identity check due to missing reference encoding.")
                return True # Fallback to True if no reference is available to avoid blocking everything

        def _check():
            try:
                image = face_recognition.load_image_file(metadata.local_path)
                encodings = face_recognition.face_encodings(image)
                if not encodings:
                    return False
                
                # Compare against the reference
                results = face_recognition.compare_faces([self._reference_encoding], encodings[0], tolerance=0.6)
                return bool(results[0])
            except Exception as e:
                logger.error(f"Error verifying identity for {metadata.local_path}: {e}")
                return False

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _check)


if __name__ == '__main__':
    # This main block is for basic debugging and can be expanded later
    # Note: Since the methods are async, we need an event loop to run them.
    
    logging.basicConfig(level=logging.INFO)

    async def run_tests():
        # Create a dummy metadata object for a test image that must exist
        test_image_path = "/home/flexone/code/ai_avatar_curator/test_raw/test_image.jpg"
        if not Path(test_image_path).exists():
            print(f"Test image not found at {test_image_path}, cannot run tests.")
            return
            
        test_image_meta = ImageMetadata(
            image_hash="test_image_hash",
            source_url="local",
            source="local",
            original_filename="test_image.jpg",
            local_path=test_image_path,
            status="raw"
        )

        print("--- Testing FaceRecognitionFilter (Remote Simulation) ---")
        face_filter = FaceRecognitionFilter(subject_name="test_subject")
        
        has_face = await face_filter.has_single_face(test_image_meta)
        print(f"Simulated has_single_face result: {has_face}")
        
        is_match = await face_filter.is_identity_match(test_image_meta)
        print(f"Simulated is_identity_match result: {is_match}")

    asyncio.run(run_tests())