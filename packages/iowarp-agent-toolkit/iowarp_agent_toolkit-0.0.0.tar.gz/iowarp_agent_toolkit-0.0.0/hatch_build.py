"""Custom Hatchling build hook for iowarp-agent-toolkit.

This hook downloads source from upstream before building the package.
"""

import sys
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Build hook to download source before building."""

    def initialize(self, version: str, build_data: dict) -> None:
        """Initialize the build hook.

        This is called before the build process starts.
        """
        # Add the project root to the Python path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))

        from build_tools import setup_build_environment

        print("Running custom build hook: downloading source from upstream...")
        setup_build_environment()
        print("Build hook complete")
