"""Color conversion helpers."""
import numpy as np


def rgb2gray(img: np.ndarray) -> np.ndarray:
    """Convert an RGB image to grayscale (returns 2D uint8 array)."""
    if img.ndim == 2:
        # Already grayscale
        return img.astype(np.uint8)
    
    # Ensure float for weighted sum
    arr = img.astype(np.float32)
    gray = arr[..., 0] * 0.2989 + arr[..., 1] * 0.5870 + arr[..., 2] * 0.1140
    return np.clip(gray, 0, 255).astype(np.uint8)


def gray2rgb(gray: np.ndarray) -> np.ndarray:
    """Convert a 2D grayscale image to 3-channel RGB."""
    if gray.ndim != 2:
        raise ValueError("Input must be a 2D grayscale image.")
    
    return np.stack([gray, gray, gray], axis=-1).astype(np.uint8)
