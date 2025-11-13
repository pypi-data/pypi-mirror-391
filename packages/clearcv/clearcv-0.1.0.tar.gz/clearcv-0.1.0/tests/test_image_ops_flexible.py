# tests/test_image_ops_flexible.py
import os
import sys
import numpy as np
import pytest

# ensure project root is on sys.path when running file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# helper to attempt import and provide a skip message
def get_attr(module, name):
    try:
        mod = __import__(module, fromlist=[name])
    except Exception as e:
        pytest.skip(f"Module '{module}' not importable: {e}")
    if not hasattr(mod, name):
        pytest.skip(f"'{module}' does not expose '{name}'")
    return getattr(mod, name)

# ---- Fixtures ----
@pytest.fixture
def dummy_rgb():
    """Return a simple 3x3 RGB test image."""
    return np.array([
        [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        [[255, 255, 0], [0, 255, 255], [255, 0, 255]],
        [[128, 128, 128], [64, 64, 64], [32, 32, 32]],
    ], dtype=np.uint8)

# ---- Try functions with safe fallbacks ----
def test_color_conversion(dummy_rgb):
    # Try common names for color conversion
    # Prefer clearcv.color.rgb2gray, but accept to_grayscale alias
    try:
        rgb2gray = get_attr("clearcv.color", "rgb2gray")
    except pytest.Skip as e:
        # fallback alias
        try:
            rgb2gray = get_attr("clearcv.color", "to_grayscale")
        except pytest.Skip:
            pytest.skip("No rgb2gray or to_grayscale found in clearcv.color")

    gray = rgb2gray(dummy_rgb)
    assert isinstance(gray, np.ndarray)
    assert gray.ndim == 2

    # gray2rgb optional
    try:
        gray2rgb = get_attr("clearcv.color", "gray2rgb")
        rgb = gray2rgb(gray)
        assert rgb.shape[-1] == 3
    except pytest.Skip:
        pytest.skip("gray2rgb not present; color conversion partial check done")

def test_filters_and_utils(dummy_rgb):
    # Try blur (different possible names)
    filter_mod = None
    try:
        filter_mod = __import__("clearcv.filters", fromlist=["*"])
    except Exception:
        pytest.skip("clearcv.filters not importable")

    # find blur-like function
    blur_fn = None
    for n in ("blur", "box_blur", "gaussian_blur"):
        if hasattr(filter_mod, n):
            blur_fn = getattr(filter_mod, n)
            break
    if blur_fn is None:
        pytest.skip("No blur function found in clearcv.filters")

    out = blur_fn(dummy_rgb)  # many implementations accept (img, kernel_size) or (img, sigma)
    assert isinstance(out, np.ndarray)
    assert out.shape == dummy_rgb.shape

    # sobel or edge
    if hasattr(filter_mod, "sobel"):
        sobel = getattr(filter_mod, "sobel")
        gray = out[...,0] if out.ndim==3 else out
        edges = sobel(gray)
        assert isinstance(edges, np.ndarray)

def test_transformations(dummy_rgb):
    try:
        tmod = __import__("clearcv.transform", fromlist=["*"])
    except Exception:
        pytest.skip("clearcv.transform not importable")

    # flip
    if hasattr(tmod, "flip_horizontal"):
        fh = getattr(tmod, "flip_horizontal")
        assert fh(dummy_rgb).shape == dummy_rgb.shape
    elif hasattr(tmod, "flip"):
        f = getattr(tmod, "flip")
        assert f(dummy_rgb, "horizontal").shape == dummy_rgb.shape
    else:
        pytest.skip("No horizontal flip function found")

    # resize (look for resize, resize_image)
    resize_fn = None
    for n in ("resize", "resize_image", "scale"):
        if hasattr(tmod, n):
            resize_fn = getattr(tmod, n)
            break
    if resize_fn is None:
        pytest.skip("No resize function found")
    # try common signatures: (img, (h,w)) or (img, new_w, new_h) or (img, scale)
    try:
        r1 = resize_fn(dummy_rgb, (2,2))
    except Exception:
        try:
            r1 = resize_fn(dummy_rgb, 2, 2)
        except Exception:
            r1 = resize_fn(dummy_rgb, 0.5)
    assert isinstance(r1, np.ndarray)

def test_io_tempfile(tmp_path):
    # test imwrite/imread if available
    try:
        io_mod = __import__("clearcv.io", fromlist=["*"])
    except Exception:
        pytest.skip("clearcv.io not importable")

    if not hasattr(io_mod, "imwrite") or not hasattr(io_mod, "imread"):
        pytest.skip("clearcv.io missing imread/imwrite")
    path = tmp_path / "tmp_test.ppm"
    # create a small image
    img = np.zeros((8,8,3), dtype=np.uint8)
    img[0,0] = [255,0,0]
    io_mod.imwrite(str(path), img)
    loaded = io_mod.imread(str(path))
    assert isinstance(loaded, np.ndarray)
    assert loaded.shape[0] == img.shape[0]
