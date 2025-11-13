import os
import numpy as np
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clearcv import io

def main():
    # Create blank image
    img = io.create_blank(100, 100, color=(255, 0, 0))
    print("Created blank image:", img.shape)

    # Save and reload it
    io.save_image("test_img.png", img)
    loaded = io.load_image("test_img.png")
    print("Loaded image shape:", loaded.shape)

    print("✅ clearcv io test passed!")

if __name__ == "__main__":
    main()
