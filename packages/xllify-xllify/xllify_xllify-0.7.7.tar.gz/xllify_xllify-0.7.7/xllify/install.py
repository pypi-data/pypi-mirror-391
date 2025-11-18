"""
xllify-install - Download and install the xllify CLI binary

This module provides functionality to download and install the xllify CLI
binary for Windows. It uses only standard library modules to minimize dependencies.
"""

import os
import sys
import platform
import zipfile
import urllib.request
import shutil
from pathlib import Path
from typing import Optional


def get_xllify_version() -> str:
    """
    Read the xllify CLI version from the XLLIFY_DIST_VERSION file.

    Returns:
        The version string (e.g., "0.7.6")
    """
    # Look for XLLIFY_DIST_VERSION file in the package root
    version_file = Path(__file__).parent.parent / "XLLIFY_DIST_VERSION"

    if not version_file.exists():
        raise FileNotFoundError(
            f"XLLIFY_DIST_VERSION file not found at {version_file}. "
            "Please ensure the file exists in the package root."
        )

    return version_file.read_text().strip()


def get_download_urls(version: Optional[str] = None) -> dict:
    """
    Get the download URLs for the xllify binaries based on platform.

    Args:
        version: Specific version to download (defaults to version from XLLIFY_DIST_VERSION)

    Returns:
        Dictionary with 'dist' and 'cli' URLs for the current platform
    """
    if version is None:
        version = get_xllify_version()

    system = platform.system()
    base_url = "https://storage.googleapis.com/xllify-action-assets"

    if system == "Windows":
        return {
            "dist": f"{base_url}/xllify-dist-v{version}-windows.zip",
            "cli": f"{base_url}/xllify-cli-v{version}-windows.zip",
        }
    elif system == "Darwin":  # macOS
        return {"cli": f"{base_url}/xllify-cli-v{version}-macos.zip"}
    else:
        raise OSError(f"Unsupported platform: {system}. Only Windows and macOS are supported.")


def get_bin_directory() -> Path:
    """
    Get the bin directory in the current virtual environment.

    Returns:
        Path to the bin/Scripts directory where executables should be installed.
    """
    # Check if we're in a virtual environment
    venv_path = os.environ.get("VIRTUAL_ENV")

    if venv_path:
        base_path = Path(venv_path)
    else:
        # Fall back to sys.prefix (works for both venv and system Python)
        base_path = Path(sys.prefix)

    # On Windows, executables go in Scripts; on Unix-like systems, in bin
    if platform.system() == "Windows":
        bin_dir = base_path / "Scripts"
    else:
        bin_dir = base_path / "bin"

    return bin_dir


def download_file(url: str, dest_path: Path, progress: bool = True) -> None:
    """
    Download a file from a URL to a destination path.

    Args:
        url: The URL to download from
        dest_path: The local path to save the file to
        progress: Whether to show download progress
    """
    print(f"Downloading from {url}...")

    with urllib.request.urlopen(url) as response:
        total_size = int(response.headers.get("content-length", 0))

        with open(dest_path, "wb") as f:
            if total_size and progress:
                downloaded = 0
                chunk_size = 8192

                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break

                    f.write(chunk)
                    downloaded += len(chunk)

                    # Show progress
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end="")

                print()  # New line after progress
            else:
                # No progress bar, just download
                shutil.copyfileobj(response, f)

    print(f"Downloaded to {dest_path}")


def extract_zip(zip_path: Path, extract_dir: Path) -> None:
    """
    Extract a zip file to a directory.

    Args:
        zip_path: Path to the zip file
        extract_dir: Directory to extract contents to
    """
    print(f"Extracting {zip_path.name}...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    print(f"Extracted to {extract_dir}")


def install_binaries_from_zip(zip_url: str, zip_name: str, bin_dir: Path, temp_dir: Path) -> None:
    """
    Download and install binaries from a zip file.

    Args:
        zip_url: URL to download the zip from
        zip_name: Name for the downloaded zip file
        bin_dir: Directory to install binaries to
        temp_dir: Temporary directory for extraction
    """
    # Download the zip file
    zip_path = temp_dir / zip_name
    download_file(zip_url, zip_path)

    # Extract the zip file to a subdirectory to avoid conflicts
    extract_subdir = temp_dir / zip_name.replace(".zip", "")
    extract_subdir.mkdir(exist_ok=True)
    extract_zip(zip_path, extract_subdir)

    # Find and move executable files to bin directory
    # On Windows, look for .exe files; on macOS/Unix, look for files without extension or with execute permission
    if platform.system() == "Windows":
        executables = list(extract_subdir.glob("*.exe"))
    else:
        # On macOS/Unix, find executable files
        executables = [f for f in extract_subdir.iterdir() if f.is_file() and os.access(f, os.X_OK)]

    if not executables:
        print(f"Warning: No executable files found in {zip_name}")
        return

    for exe_file in executables:
        dest_path = bin_dir / exe_file.name

        # Remove existing file if it exists
        if dest_path.exists():
            print(f"Removing existing {dest_path.name}...")
            dest_path.unlink()

        # Move the executable to bin directory
        shutil.move(str(exe_file), str(dest_path))

        # Ensure it's executable on Unix-like systems
        if platform.system() != "Windows":
            dest_path.chmod(0o755)

        print(f"Installed {exe_file.name} to {dest_path}")


def install_binary(version: Optional[str] = None, custom_urls: Optional[dict] = None) -> None:
    """
    Download and install the xllify binaries for the current platform.

    Args:
        version: Specific version to install (defaults to version from XLLIFY_DIST_VERSION)
        custom_urls: Custom URLs dict to download from (overrides version-based URLs)
    """
    if version is None:
        version = get_xllify_version()

    if custom_urls is None:
        download_urls = get_download_urls(version)
    else:
        download_urls = custom_urls

    # Get the bin directory
    bin_dir = get_bin_directory()
    bin_dir.mkdir(parents=True, exist_ok=True)

    system = platform.system()
    print(f"Installing xllify v{version} for {system} to {bin_dir}")

    # Create a temporary directory for download
    temp_dir = bin_dir / ".xllify-install-temp"
    temp_dir.mkdir(exist_ok=True)

    try:
        # Install dist binary (Windows only)
        if "dist" in download_urls:
            print("\nInstalling xllify-dist...")
            install_binaries_from_zip(download_urls["dist"], "xllify-dist.zip", bin_dir, temp_dir)

        # Install CLI binary (all platforms)
        if "cli" in download_urls:
            print("\nInstalling xllify-cli...")
            install_binaries_from_zip(download_urls["cli"], "xllify-cli.zip", bin_dir, temp_dir)

        print("\n✓ Installation complete!")
        print(f"\nThe xllify binaries are now available in your PATH at:")
        print(f"  {bin_dir}")

        # Check if bin directory is in PATH
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        if str(bin_dir) not in path_dirs:
            print("\nWarning: The bin directory may not be in your PATH.")
            print("If you're using a virtual environment, make sure it's activated.")

    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def main() -> None:
    """Main entry point for the xllify-install command."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download and install the xllify binaries for your platform"
    )
    parser.add_argument(
        "--version",
        help="Specific version to install (default: read from XLLIFY_DIST_VERSION)",
        default=None,
    )
    parser.add_argument(
        "--dist-url", help="Custom download URL for xllify-dist (Windows only)", default=None
    )
    parser.add_argument("--cli-url", help="Custom download URL for xllify-cli", default=None)

    args = parser.parse_args()

    try:
        custom_urls = None
        if args.dist_url or args.cli_url:
            custom_urls = {}
            if args.dist_url:
                custom_urls["dist"] = args.dist_url
            if args.cli_url:
                custom_urls["cli"] = args.cli_url

        install_binary(version=args.version, custom_urls=custom_urls)
    except Exception as e:
        print(f"\nError during installation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
