import pytest
import cv2
import numpy as np
from pathlib import Path

from src.processors.image_processor import ImageProcessor
from src.schemas import ImageMetadata, FaceMetrics

@pytest.fixture(scope="module")
def temp_proc_dir(tmpdir_factory):
    """Create a temporary directory for processed test images."""
    return Path(tmpdir_factory.mktemp("processed_images"))

@pytest.fixture(scope="module")
def source_image(tmpdir_factory):
    """Create a source image for processing tests."""
    path = Path(tmpdir_factory.mktemp("source_images")) / "source.jpg"
    # Create a 1024x768 image
    img = np.random.randint(0, 255, size=(768, 1024, 3), dtype=np.uint8)
    cv2.imwrite(str(path), img)
    return str(path)

@pytest.fixture
def image_processor(temp_proc_dir):
    """Returns an ImageProcessor instance."""
    return ImageProcessor(output_dir=str(temp_proc_dir), target_size=512)

def test_process_image_creates_file(image_processor, source_image):
    """Test that process_image successfully creates a new file."""
    metadata = ImageMetadata(
        image_hash="test_proc_hash", 
        source_url="test", 
        source="test", 
        original_filename="source.jpg", 
        local_path=source_image,
        face_metrics=FaceMetrics(
            bounding_box=(200, 800, 600, 400),
            face_size=400,
            sharpness_score=150.0
        )
    )
    
    output_path = image_processor.process_image(metadata)
    
    assert Path(output_path).exists()
    assert Path(output_path).name == "test_proc_hash.png"

def test_processed_image_has_correct_size(image_processor, source_image):
    """Test that the processed image is resized to the target size."""
    metadata = ImageMetadata(
        image_hash="test_resize_hash", 
        source_url="test", 
        source="test", 
        original_filename="source.jpg", 
        local_path=source_image,
        face_metrics=FaceMetrics(
            bounding_box=(200, 800, 600, 400),
            face_size=400,
            sharpness_score=150.0
        )
    )
    
    output_path = image_processor.process_image(metadata)
    
    processed_image = cv2.imread(output_path)
    height, width, _ = processed_image.shape
    
    assert height == image_processor.target_size
    assert width == image_processor.target_size

def test_smart_crop_logic(image_processor):
    """Test the internal smart cropping logic."""
    image = np.zeros((1000, 800, 3), dtype=np.uint8)
    # A 100x100 face box in the center
    face_location = (450, 450, 550, 350) # t, r, b, l
    
    image_processor.crop_scale = 2.0
    cropped = image_processor._smart_crop(image, face_location)
    
    # Expected crop size = max(100, 100) * 2.0 = 200
    # Center is at (400, 500)
    # Expected crop: top=400, left=300, bottom=600, right=500
    height, width, _ = cropped.shape
    assert height == 200
    assert width == 200
