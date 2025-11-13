"""Very small set of geometric transforms (nearest-neighbor)."""
import numpy as np


def resize(img: np.ndarray, new_w: int, new_h: int) -> np.ndarray:
    """Resize image to (new_h, new_w) using nearest-neighbor sampling."""
    h, w = img.shape[:2]
    row_idx = np.linspace(0, h - 1, new_h).astype(int)
    col_idx = np.linspace(0, w - 1, new_w).astype(int)
    if img.ndim == 3:
        return img[row_idx[:, None], col_idx[None, :], :]
    return img[row_idx[:, None], col_idx[None, :]]


def flip_horizontal(img: np.ndarray) -> np.ndarray:
    """Flip image horizontally (mirror left↔right)."""
    return img[:, ::-1]


def flip_vertical(img: np.ndarray) -> np.ndarray:
    """Flip image vertically (mirror top↔bottom)."""
    return img[::-1, :]


def rotate90(img: np.ndarray, k: int = 1) -> np.ndarray:
    """Rotate image by 90 degrees k times (k can be negative)."""
    k = k % 4
    return np.rot90(img, k)


def crop(img: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    """Crop image to region (x, y, w, h)."""
    return img[y:y + h, x:x + w]
