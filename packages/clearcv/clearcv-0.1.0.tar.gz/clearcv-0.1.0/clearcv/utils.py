"""Helpers for normalization and display (optional matplotlib)."""
import numpy as np


def normalize(img: np.ndarray) -> np.ndarray:
    """Normalize image values to full 0–255 uint8 range."""
    arr = img.astype(np.float32)
    mn = arr.min()
    arr -= mn
    mx = arr.max()
    if mx != 0:
        arr = arr / mx * 255.0
    return np.clip(arr, 0, 255).astype(np.uint8)


def ensure_rgb(img: np.ndarray) -> np.ndarray:
    """Ensure image is 3-channel RGB (convert grayscale if needed)."""
    if img.ndim == 2:  # grayscale
        return np.stack([img, img, img], axis=-1).astype(np.uint8)
    elif img.ndim == 3 and img.shape[2] == 3:
        return img.astype(np.uint8)
    else:
        raise ValueError(f"Unsupported image shape: {img.shape}")


def show(img: np.ndarray, title: str = "Image"):
    """Display an image using matplotlib, if available."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — cannot display image.")
        return

    rgb = ensure_rgb(img)
    plt.imshow(rgb)
    plt.title(title)
    plt.axis("off")
    plt.show()
