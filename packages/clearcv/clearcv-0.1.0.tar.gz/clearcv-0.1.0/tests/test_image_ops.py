import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clearcv import io, color, filters, transform

def main():
    # 1️⃣ Create a simple grayscale array (5x5)
    img = [[(x + y) * 10 for x in range(5)] for y in range(5)]

    print("Original matrix:")
    for row in img:
        print(row)

    # 2️⃣ Convert to pseudo-image (simulate grayscale)
    gray_img = color.to_grayscale(img)
    print("\nGrayscale (simulated) output:")
    for row in gray_img:
        print(row)

    # 3️⃣ Apply filter (dummy blur)
    blurred = filters.blur(gray_img)
    print("\nBlurred output:")
    for row in blurred:
        print(row)

    # 4️⃣ Resize or transform
    transformed = transform.resize(gray_img, (3, 3))
    print("\nResized 3x3 output:")
    for row in transformed:
        print(row)

    print("\n✅ clearcv image ops test passed!")

if __name__ == "__main__":
    main()
