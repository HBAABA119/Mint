"""
Prim Platform Support
Provides platform detection, platform-specific code, cross-platform support,
platform configuration, and platform management.
"""

import platform
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Platform(Enum):
    """Platforms"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    ANDROID = "android"
    IOS = "ios"


@dataclass
class PlatformInfo:
    """Platform information"""
    platform: Platform
    version: str
    arch: str


class PlatformManager:
    """Platform manager"""

    def __init__(self):
        self.platform = self._detect_platform()

    def _detect_platform(self) -> Platform:
        """Detect current platform"""
        system = platform.system().lower()
        if system == "windows":
            return Platform.WINDOWS
        elif system == "linux":
            return Platform.LINUX
        elif system == "darwin":
            return Platform.MACOS
        return Platform.LINUX

    def get_info(self) -> PlatformInfo:
        """Get platform info"""
        return PlatformInfo(
            platform=self.platform,
            version=platform.release(),
            arch=platform.machine()
        )


def main():
    print("Testing Platform Support...")
    manager = PlatformManager()
    info = manager.get_info()
    print(f"Platform: {info.platform.value}")
    print("Platform Support initialized successfully")


if __name__ == "__main__":
    main()
