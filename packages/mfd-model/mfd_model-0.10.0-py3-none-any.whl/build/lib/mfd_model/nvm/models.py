# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Data structures for MFD NVM Manager module."""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, constr, ConfigDict, model_validator, field_validator

MANDATORY_UPLOAD_FIELDS = ["eetrackid", "family", "release", "four_part_id"]

eetrack_str = constr(pattern="[0-9a-fA-F]{8}", min_length=8, max_length=8)
hex_id_four_chars = constr(pattern="[0-9a-fA-F]{4}", min_length=4, max_length=4)


class StrictBaseModel(BaseModel):
    """Base model with extra fields ignored."""

    model_config = ConfigDict(extra="ignore")


class FourPartID(StrictBaseModel):
    """Pydantic model for sub/vendor + sub/device."""

    vendor: hex_id_four_chars | None = None
    subvendor: hex_id_four_chars | None = None
    device: hex_id_four_chars | None = None
    subdevice: hex_id_four_chars | None = None

    @field_validator("vendor", "subvendor", "device", "subdevice", mode="after")
    @classmethod
    def uppercase_fourpart_id(cls: "FourPartID", value: str) -> str:
        """Convert fourpartid to uppercase."""
        return value.upper()


class Release(StrictBaseModel):
    """Pydantic model for the release."""

    release: str
    milestone: Literal["Alpha", "Beta", "PC", "PV"] | None = None
    drop: str | None = None


class CommonNVMParams(StrictBaseModel):
    """Common NVM parameters for download and upload endpoints."""

    devicename: str | None = None
    eetrackid: eetrack_str | None = None
    family: Literal["Columbiaville", "Fortville", "Connorsville", "Linkville"] | None = None
    four_part_id: FourPartID | None = None
    metadata: dict[str, str] = {}
    pldm_header: bool | None = None
    release: list[Release] = []
    replaces: list[eetrack_str] = []
    signed: bool | None = None

    @field_validator("eetrackid", mode="after")
    @classmethod
    def uppercase_eetrackid(cls: "CommonNVMParams", value: str) -> str:
        """Convert eetrackid to uppercase."""
        return value.upper()

    @field_validator("replaces", mode="after")
    @classmethod
    def uppercase_replaces(cls: "CommonNVMParams", value: list[str]) -> list[str]:
        """Convert replaces eetrackid to uppercase."""
        return [repl.upper() for repl in value]


class NVMParams(CommonNVMParams):
    """Pydantic model for the Body parameters of the file download endpoint."""

    url: str | None = None
    md5_checksum: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls: NVMParams, value: dict | str) -> NVMParams | dict:
        """
        Cast string to a model.

        To send nested model as a body of POST together with a file
        we need to send it as a string and cast it back on server side.
        """
        if isinstance(value, str):
            return cls(**json.loads(value))
        else:
            return value


class NVMUploadParams(CommonNVMParams):
    """Pydantic model for Query parameters for file upload endpoint."""

    pldm_header: bool = True
    signed: bool = True

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls: NVMUploadParams, value: dict | str) -> NVMUploadParams | dict:
        """
        Cast string to a model.

        To send nested model as a body of POST together with a file
        we need to send it as a string and cast it back on server side.
        """
        if isinstance(value, str):
            return cls(**json.loads(value))

        four_part_id_filled_elems = (
            len(value.get("four_part_id").model_dump(exclude_none=True))
            if isinstance(value.get("four_part_id"), FourPartID)
            else len([k for k, v in value.get("four_part_id", {}).items() if v])
        )

        # validate if all mandatory fields are present in Upload Params
        if (
            any(f not in value for f in MANDATORY_UPLOAD_FIELDS) or four_part_id_filled_elems != 4  # all fields set
        ):
            raise ValueError(
                "Mandatory fields are missing in the request.\n"
                f"\tMandatory fields: {MANDATORY_UPLOAD_FIELDS}\n"
                f"\tPassed fields: {list(value)}"
            )

        return value
