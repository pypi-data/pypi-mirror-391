# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Data structures for MFD Artifacts Manager module."""

from enum import Enum
from typing import Literal

SUPPORTED_EXTENSIONS = Literal["zip", "tar", "tar.gz"]


class DownloadStatus(Enum):
    """Download status enum."""

    QUEUED = "QUEUED"
    DOWNLOADING_FROM_SHARE = "DOWNLOADING FROM SHARE..."
    MAKING_AN_ARCHIVE = "MAKING AN ARCHIVE..."
    READY = "READY"
