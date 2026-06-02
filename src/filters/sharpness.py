import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_sharpness(image: np.ndarray) -> float:
    """
    Calculate the sharpness of an image using the Laplacian variance method.
    
    Args:
        image: A numpy array representing the image (BGR format from cv2).
        
    Returns:
        The variance of the Laplacian of the image. Higher values mean sharper.
    """
    if image is None:
        return 0.0
        
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculate Laplacian
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    return float(laplacian_var)

def is_sharp(image: np.ndarray, threshold: float = 100.0) -> bool:
    """
    Check if an image is sharp enough based on a threshold.
    """
    return calculate_sharpness(image) >= threshold
