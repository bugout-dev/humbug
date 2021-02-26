"""
This module implements methods related to retrieving information about the user's operating system,
computer, and Python runtime.
"""

from dataclasses import dataclass
import platform


@dataclass
class SystemInformation:
    os: str
    os_release: str
    machine: str
    processor: str
    python_version: str
    python_version_major: str
    python_version_minor: str
    python_version_patch: str


def generate() -> SystemInformation:
    """
    Generates a system information object for the user's system.
    """
    platform_info = platform.uname()
    major, minor, patch = platform.python_version_tuple()
    return SystemInformation(
        os=platform_info.system,
        os_release=platform_info.release,
        machine=platform_info.machine,
        processor=platform_info.processor,
        python_version=platform.python_version(),
        python_version_major=major,
        python_version_minor=minor,
        python_version_patch=patch,
    )
