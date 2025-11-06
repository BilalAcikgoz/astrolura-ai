import os
import urllib.request
import sys
from pathlib import Path

# Swiss Ephemeris download URLs - using GitHub mirror
EPHE_BASE_URL = "https://github.com/aloistr/swisseph/raw/master/ephe/"

# Required ephemeris files (covers 1800-2399)
REQUIRED_FILES = [
    # This file contains all planets including Sun, Moon, and major planets
    "seplm18.se1",  # Planets long period 1800-2399 (includes all needed data)
]

# Additional optional files for higher precision
OPTIONAL_FILES = [
    "semom18.se1",  # Moon Moshier (high precision, optional)
]

def download_file(url: str, dest_path: Path):
    # Download a file from URL to destination path
    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, dest_path)
        print(f"  ✓ Saved to {dest_path}")
        return True
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


def main():
    # Download ephemeris files
    # Get ephemeris directory from environment or use default
    ephe_dir = os.getenv("EPHE_PATH", "./ephe")
    ephe_path = Path(ephe_dir)

    # Create directory if it doesn't exist
    ephe_path.mkdir(parents=True, exist_ok=True)
    print(f"Ephemeris directory: {ephe_path.absolute()}\n")

    # Download required files
    print("Downloading required ephemeris files...")
    required_success = 0
    for filename in REQUIRED_FILES:
        url = EPHE_BASE_URL + filename
        dest = ephe_path / filename

        if dest.exists():
            print(f"  ⊙ {filename} already exists, skipping")
            required_success += 1
            continue

        if download_file(url, dest):
            required_success += 1

    print(f"\nRequired files: {required_success}/{len(REQUIRED_FILES)}")

    print("\n" + "="*50)
    if required_success == len(REQUIRED_FILES):
        print("✓ All required ephemeris files are ready!")
        print(f"  Path: {ephe_path.absolute()}")
        print("\nYou can now run the application.")
        return 0
    else:
        print("✗ Some required files failed to download.")
        print("  Please check your internet connection and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
