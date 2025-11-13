import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clearcv import __version__

def main():
    print("✅ clearcv basic test passed!")
    print(f"Version: {__version__}")

if __name__ == "__main__":
    main()
