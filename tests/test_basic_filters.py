import pytest
import cv2
import numpy as np
from pathlib import Path

from src.filters.basic_filters import BasicFilter

@pytest.fixture(scope="module")
def temp_image_dir(tmpdir_factory):
    """Create a temporary directory for test images."""
    return Path(tmpdir_factory.mktemp("test_images"))

@pytest.fixture(scope="module")
def sharp_image(temp_image_dir):
    """Create a sharp, high-resolution image."""
    path = temp_image_dir / "sharp.jpg"
    # Create a noisy image which has a high Laplacian variance
    img = np.random.randint(0, 255, size=(600, 600, 3), dtype=np.uint8)
    cv2.imwrite(str(path), img)
    return str(path)

@pytest.fixture(scope="module")
def blurry_image(temp_image_dir):
    """Create a blurry, high-resolution image."""
    path = temp_image_dir / "blurry.jpg"
    img = np.zeros((600, 600, 3), dtype=np.uint8)
    # A flat image will have zero variance
    cv2.imwrite(str(path), img)
    return str(path)

@pytest.fixture(scope="module")
def low_res_image(temp_image_dir):
    """Create a sharp, low-resolution image."""
    path = temp_image_dir / "low_res.jpg"
    img = np.random.randint(0, 255, size=(300, 300, 3), dtype=np.uint8)
    cv2.imwrite(str(path), img)
    return str(path)

@pytest.fixture(scope="module")
def dark_image(temp_image_dir):
    """Create an image that is too dark."""
    path = temp_image_dir / "dark.jpg"
    img = np.full((600, 600, 3), 10, dtype=np.uint8)
    cv2.imwrite(str(path), img)
    return str(path)

@pytest.fixture(scope="module")
def bright_image(temp_image_dir):
    """Create an image that is too bright."""
    path = temp_image_dir / "bright.jpg"
    img = np.full((600, 600, 3), 250, dtype=np.uint8)
    cv2.imwrite(str(path), img)
    return str(path)

def test_is_sharp(sharp_image):
    """Test that a sharp image passes the sharpness filter."""
    basic_filter = BasicFilter(sharpness_threshold=100.0)
    assert basic_filter.is_sharp(sharp_image)

def test_is_not_sharp(blurry_image):
    """Test that a blurry image fails the sharpness filter."""
    basic_filter = BasicFilter(sharpness_threshold=100.0)
    assert not basic_filter.is_sharp(blurry_image)

def test_is_high_resolution(sharp_image):
    """Test that a high-resolution image passes the resolution filter."""
    basic_filter = BasicFilter(min_resolution=512)
    assert basic_filter.is_high_resolution(sharp_image) is True

def test_is_not_high_resolution(low_res_image):
    """Test that a low-resolution image fails the resolution filter."""
    basic_filter = BasicFilter(min_resolution=512)
    assert basic_filter.is_high_resolution(low_res_image) is False

def test_is_well_lit(sharp_image):
    """Test that a well-lit image passes the brightness filter."""
    basic_filter = BasicFilter(brightness_range=(40, 240))
    assert basic_filter.is_well_lit(sharp_image) is True

def test_is_not_well_lit_dark(dark_image):
    """Test that a dark image fails the brightness filter."""
    basic_filter = BasicFilter(brightness_range=(40, 240))
    assert basic_filter.is_well_lit(dark_image) is False

def test_is_not_well_lit_bright(bright_image):
    """Test that a bright image fails the brightness filter."""
    basic_filter = BasicFilter(brightness_range=(40, 240))
    assert basic_filter.is_well_lit(bright_image) is False

def test_apply_all_passes(sharp_image):
    """Test that a good image passes all basic filters."""
    from src.schemas import ImageMetadata
    metadata = ImageMetadata(image_hash="sharp", source_url="test", source="test", original_filename="sharp.jpg", local_path=sharp_image)
    basic_filter = BasicFilter(min_resolution=512, sharpness_threshold=100.0)
    assert basic_filter.apply_all(metadata) is True

def test_apply_all_fails_sharpness(blurry_image):
    """Test that a blurry image fails the combined filter check."""
    from src.schemas import ImageMetadata
    metadata = ImageMetadata(image_hash="blurry", source_url="test", source="test", original_filename="blurry.jpg", local_path=blurry_image)
    basic_filter = BasicFilter(min_resolution=512, sharpness_threshold=100.0)
    assert basic_filter.apply_all(metadata) is False

def test_apply_all_fails_resolution(low_res_image):
    """Test that a low-resolution image fails the combined filter check."""
    from src.schemas import ImageMetadata
    metadata = ImageMetadata(image_hash="low_res", source_url="test", source="test", original_filename="low_res.jpg", local_path=low_res_image)
    basic_filter = BasicFilter(min_resolution=512, sharpness_threshold=100.0)
    assert basic_filter.apply_all(metadata) is False
