from typing import Tuple, Optional
import numpy as np

def validate_resolution(
    image: np.ndarray, 
    min_resolution: Tuple[int, int] = (512, 512)
) -> bool:
    """
    Check if the image meets the minimum resolution requirements.
    """
    if image is None:
        return False
        
    height, width = image.shape[:2]
    return width >= min_resolution[0] and height >= min_resolution[1]

def get_aspect_ratio(image: np.ndarray) -> float:
    """
    Calculate the aspect ratio (width / height) of the image.
    """
    if image is None:
        return 0.0
        
    height, width = image.shape[:2]
    return width / height

def is_portrait_or_square(image: np.ndarray, tolerance: float = 0.2) -> bool:
    """
    Check if the image is portrait or square-ish.
    Portrait/Square usually has aspect ratio <= 1.0 + tolerance.
    """
    ar = get_aspect_ratio(image)
    return ar <= (1.0 + tolerance)
