# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Models for MFD Artifacts Manager module."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal

from mfd_const.artifacts_manager import Artifacts
from mfd_const.artifacts_manager.models import Artifact
from pydantic import BaseModel, model_validator

from mfd_model.artifacts_manager.data_structures import DownloadStatus, SUPPORTED_EXTENSIONS


class ArtifactInfo(BaseModel):
    """Artifact information."""

    name: str
    version: str


class ContainerInfo(BaseModel):
    """Container information."""

    name: str
    tics: list[int]


class ArtifactVersionInfo(BaseModel):
    """Artifact version information."""

    version: str
    containers: list[ContainerInfo]


class ReleaseInfo(BaseModel):
    """Release information."""

    tics: list[int]
    versions: list[str]


class ArtifactPathInfo(BaseModel):
    """Artifact path information."""

    artifact_path: Path
    desired_name: str


class DownloadRequest(BaseModel):
    """Download request information."""

    type: Literal["comp_lib"]
    artifacts: list[ArtifactPathInfo]
    archive_name: str
    archive_extension: SUPPORTED_EXTENSIONS = "zip"


class BuildDownloadInfo(BaseModel):
    """Build download information."""

    filename: str  # name which will be used to save the file on the client side
    extension: str
    path: Path | None = None  # path to the compressed archive on the server, filled after archive creation
    last_download_date: datetime = datetime.now()
    status: DownloadStatus = DownloadStatus.QUEUED


class ArtifactRequest(BaseModel):
    """Request for artifact download."""

    artifact: Artifact | str  # Artifact object or comp lib name accepted
    version: str | None = None
    tic: int | None = None
    os: Enum | str | None = None  # COMMON_SUPPORTED_OS, Artifact specific OS Enum or str with Enum name accepted

    @model_validator(mode="before")  # "before" validators are executed from the bottom, this will execute 2nd
    @classmethod
    def validate_os_and_cast_to_str(cls: ArtifactRequest, data: dict) -> dict:
        """Check if OS is supported, change OS object to string."""
        if data.get("os") is None:
            return data

        supported_oses = Artifacts.get_artifact(data["artifact"]).os

        if isinstance(data["os"], Artifacts.COMMON_SUPPORTED_OS):
            data["os"] = getattr(supported_oses, data["os"].name, None)
        elif isinstance(data["os"], str):  # Enum name
            data["os"] = getattr(supported_oses, data["os"], None)

        if data["os"] is None or data["os"] not in supported_oses.__members__.values():
            raise ValueError(
                f"OS not supported by {data['artifact']}.\nSupported OSes: {list(supported_oses.__members__)}"
            )

        data["os"] = data["os"].value

        return data

    @model_validator(mode="before")  # "before" validators are executed from the bottom, this will execute 1st
    @classmethod
    def validate_artifact_and_cast_to_str(cls: ArtifactRequest, data: dict) -> dict:
        """Check if artifact is supported and change Artifact object to comp lib name."""
        if isinstance(data.get("artifact"), Artifact):
            data["artifact"] = data["artifact"].comp_lib_name
        else:
            Artifacts.get_artifact(data["artifact"])  # check if artifact is valid

        return data
