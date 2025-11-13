"""I/O helpers — supports PPM (P6) by default and optional imageio for other formats."""

from typing import Optional
import numpy as np


def _read_ppm(path: str) -> np.ndarray:
    """Read a binary PPM (P6) image into a NumPy array."""
    with open(path, 'rb') as f:
        header = f.readline().decode().strip()
        if header != 'P6':
            raise ValueError('Only binary PPM (P6) supported by _read_ppm')

        # Read dimensions and maxval, skipping comments
        dims = f.readline().decode()
        while dims.startswith('#'):
            dims = f.readline().decode()

        width, height = map(int, dims.split())
        maxval = int(f.readline().decode())

        data = f.read()
        arr = np.frombuffer(data, dtype=np.uint8)
        img = arr.reshape((height, width, 3)).copy()
        return img


def _write_ppm(path: str, img: np.ndarray):
    """Write a NumPy array as a binary PPM (P6) image."""
    h, w = img.shape[:2]
    with open(path, 'wb') as f:
        f.write(b'P6\n')
        f.write(f"{w} {h}\n255\n".encode())
        f.write(img.astype(np.uint8).tobytes())


def imread(path: str) -> np.ndarray:
    """Read an image from path.
    If imageio is installed it will be used for richer formats.
    Otherwise, PPM is supported natively.
    """
    try:
        import imageio
    except Exception:
        imageio = None

    if imageio is not None:
        img = imageio.imread(path)
        # imageio may load grayscale as 2D — normalize into 3-channel when needed
        if img.ndim == 2:
            img = np.stack([img, img, img], axis=-1)
        return img.astype(np.uint8)

    # fallback: support only .ppm using internal reader
    return _read_ppm(path)


def imwrite(path: str, img: np.ndarray):
    """Write an image.
    If imageio is installed it will be used.
    Otherwise, writes PPM.
    """
    try:
        import imageio
    except Exception:
        imageio = None

    if imageio is not None:
        imageio.imwrite(path, img.astype(np.uint8))
        return

    # fallback: write ppm
    _write_ppm(path, img)
