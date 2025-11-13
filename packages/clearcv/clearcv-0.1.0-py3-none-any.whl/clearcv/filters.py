"""Convolutional filters implemented with NumPy (no SciPy required)."""
import numpy as np
from typing import Tuple


def _pad2d(arr: np.ndarray, pad_h: int, pad_w: int) -> np.ndarray:
    """Pad a 2D array symmetrically using edge padding."""
    return np.pad(arr, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')


def convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Perform 2D convolution (single-channel) using pure NumPy.

    Args:
        image: 2D array (H x W)
        kernel: 2D small array (kh x kw)

    Returns:
        Same-shape 2D array (float32)
    """
    kh, kw = kernel.shape
    assert kh % 2 == 1 and kw % 2 == 1, "Kernel must have odd dimensions"

    pad_h = kh // 2
    pad_w = kw // 2
    padded = _pad2d(image, pad_h, pad_w)

    H, W = image.shape
    out = np.zeros_like(image, dtype=np.float32)

    # flip kernel for convolution
    k = np.flipud(np.fliplr(kernel))
    for y in range(H):
        for x in range(W):
            region = padded[y:y + kh, x:x + kw]
            out[y, x] = np.sum(region * k)

    return out


def _apply_kernel_rgb(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Apply a convolution kernel to each channel of an RGB image."""
    out = np.zeros_like(img, dtype=np.float32)
    for c in range(img.shape[2]):
        out[..., c] = convolve2d(img[..., c].astype(np.float32), kernel)
    return np.clip(out, 0, 255).astype(np.uint8)


def box_blur(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Apply a simple box blur (mean filter) to an RGB image."""
    k = np.ones((kernel_size, kernel_size), dtype=np.float32)
    k /= (kernel_size * kernel_size)
    return _apply_kernel_rgb(img, k)


def sobel(gray: np.ndarray) -> np.ndarray:
    """Sobel edge detector for a single-channel grayscale image.

    Returns:
        uint8 array of gradient magnitude.
    """
    if gray.ndim != 2:
        raise ValueError("Sobel expects a 2D grayscale image")

    Kx = np.array([[1, 0, -1],
                   [2, 0, -2],
                   [1, 0, -1]], dtype=np.float32)
    Ky = np.array([[1, 2, 1],
                   [0, 0, 0],
                   [-1, -2, -1]], dtype=np.float32)

    gx = convolve2d(gray.astype(np.float32), Kx)
    gy = convolve2d(gray.astype(np.float32), Ky)

    mag = np.hypot(gx, gy)
    mag = (mag / mag.max()) * 255 if mag.max() != 0 else mag

    return np.clip(mag, 0, 255).astype(np.uint8)
