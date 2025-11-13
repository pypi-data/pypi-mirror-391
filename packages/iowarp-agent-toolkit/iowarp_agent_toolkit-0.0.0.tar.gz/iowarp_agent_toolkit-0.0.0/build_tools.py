"""Build tools for iowarp-agent-toolkit package.

This module handles downloading source from the upstream agent-toolkit
repository during package build.
"""

import os
import shutil
import tarfile
import tempfile
from pathlib import Path
from urllib.request import urlretrieve


AGENT_TOOLKIT_VERSION = "main"
AGENT_TOOLKIT_URL = f"https://github.com/iowarp/agent-toolkit/archive/refs/heads/{AGENT_TOOLKIT_VERSION}.tar.gz"

# Directories to include from upstream
INCLUDE_DIRS = [
    "agent-toolkit-mcp-servers",
    "agent-toolkit-ai-devkit",
    "agent-toolkit-mcp-clients",
]


def download_and_extract_source(target_dir: Path) -> None:
    """Download and extract source from upstream agent-toolkit repository.

    Args:
        target_dir: Directory to extract source files into
    """
    print(f"Downloading source from {AGENT_TOOLKIT_URL}")

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
        try:
            # Download tarball
            urlretrieve(AGENT_TOOLKIT_URL, tmp_file.name)
            print(f"Downloaded to {tmp_file.name}")

            # Extract to temporary directory
            with tempfile.TemporaryDirectory() as tmp_dir:
                print(f"Extracting to {tmp_dir}")
                with tarfile.open(tmp_file.name, "r:gz") as tar:
                    tar.extractall(tmp_dir)

                # Find the extracted directory (should be agent-toolkit-main)
                extracted_dirs = list(Path(tmp_dir).iterdir())
                if not extracted_dirs:
                    raise RuntimeError("No directory found after extraction")

                source_root = extracted_dirs[0]
                print(f"Source root: {source_root}")

                # Copy specified directories to target
                target_dir.mkdir(parents=True, exist_ok=True)

                for dir_name in INCLUDE_DIRS:
                    source_path = source_root / dir_name
                    target_path = target_dir / dir_name

                    if source_path.exists():
                        print(f"Copying {dir_name} to {target_path}")
                        if target_path.exists():
                            shutil.rmtree(target_path)
                        shutil.copytree(source_path, target_path)
                    else:
                        print(f"Warning: {dir_name} not found in source")

                print("Source download and extraction complete")

        finally:
            # Clean up temporary tarball
            if os.path.exists(tmp_file.name):
                tmp_file.close()
                os.unlink(tmp_file.name)


def setup_build_environment() -> None:
    """Set up build environment by downloading source if needed."""
    # Determine the project root directory
    project_root = Path(__file__).parent

    # Check if source directories already exist
    all_exist = all(
        (project_root / dir_name).exists()
        for dir_name in INCLUDE_DIRS
    )

    if not all_exist:
        print("Source directories not found, downloading from upstream...")
        download_and_extract_source(project_root)
    else:
        print("Source directories already exist, skipping download")


if __name__ == "__main__":
    setup_build_environment()
