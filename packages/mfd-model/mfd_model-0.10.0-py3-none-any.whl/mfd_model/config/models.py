# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Topology models."""

from __future__ import annotations

import logging
from typing import Any, Literal

from mfd_common_libs import add_logging_level, log_levels
from mfd_typing.data_structures import IPUHostType
from packaging.version import Version
from pydantic import Field, IPvAnyAddress, BaseModel, field_validator, model_validator, SecretStr

from mfd_model.config.__version__ import VERSION

logger = logging.getLogger(__name__)
add_logging_level(level_name="MODULE_DEBUG", level_value=log_levels.MODULE_DEBUG)


class InstantiateBaseModel(BaseModel, extra="forbid"):
    """Instantiate Base Model."""

    instantiate: bool = Field(True, description="Determines whether fixture shall instantiate object or skip it")


class SchemaMetadata(BaseModel, extra="forbid"):
    """Schema version."""

    version: str

    @field_validator("version")
    @classmethod
    def version_must_fit(cls: SchemaMetadata, v: str) -> str:
        """Check if version is right."""
        if Version(v).major != Version(VERSION).major:
            raise ValueError(f"Wrong schema version: '{v}', Expected '{Version(VERSION).major}'.* ")
        return v


class IPModel(BaseModel, extra="forbid"):
    """IP Address model."""

    value: IPvAnyAddress = None
    mask: int | None = None

    @model_validator(mode="after")
    def validate_value(self) -> IPModel:
        """Check whether all fields are provided."""
        if self.value is None:
            raise ValueError("Mandatory field 'value' is missing.")
        return self


class OSDControllerModel(BaseModel, extra="forbid"):
    """OSD Controller model."""

    base_url: str
    username: str | None = None
    password: str | None = None
    secured: bool | None = True
    proxies: dict[str, str] | None = None

    @field_validator("password")
    @classmethod
    def change_password_field_to_secretstr(cls: OSDControllerModel, v: str) -> SecretStr:
        """Change password to SecretStr object for security."""
        if v is not None:
            return SecretStr(v)


class ConnectionModelBase(BaseModel, extra="forbid"):
    """RPC Connection model."""

    connection_id: int = 0
    ip_address: IPvAnyAddress | None = None
    mac_address: str | None = None  # can be replaced with pydantic_extra_types(2.1+)/MacAddress, after Pydantic update
    connection_type: str
    connection_options: dict | None = None
    relative_connection_id: int | None = None
    osd_details: OSDControllerModel | None = None


class PowerMngModelBase(BaseModel, extra="forbid"):
    """Power model."""

    power_mng_type: str
    connection: ConnectionModelBase | None = None
    host: str | None = None
    ip: str | None = None
    username: str | None = None
    password: SecretStr | None = None
    udp_port: int | None = None
    community_string: str | None = None
    outlet_number: int | None = None


class MachineModel(InstantiateBaseModel, extra="forbid"):
    """Machine model."""

    name: str = None
    mng_ip_address: IPvAnyAddress | None = None  # BMC MNG Address or Switch IP address
    mng_user: str | None = None
    mng_password: SecretStr | None = None
    power_mng: PowerMngModelBase | None = None


class SwitchModelBase(MachineModel, extra="forbid"):
    """Switch model."""

    switch_type: str = Field(description="Accepts name of any Switch Class available in MFD-Switchmanagement")
    device_type: str | None = None
    connection_type: str = Field(
        description="Accepts name of any Switch Connection Class available in MFD-Switchmanagement"
    )
    ssh_key_file: str | None = None
    use_ssh_key: bool | None = None
    enable_password: SecretStr | None = None
    auth_timeout: int | None = None
    switch_ports: list[str] | None = None
    vlans: list[str] | None = None
    switch_object: Any = None


class NetworkInterfaceModelBase(InstantiateBaseModel, extra="forbid"):
    """Single interface of NIC."""

    pci_address: str | None = Field(
        None,
        description="PCI Address (hexadecimal or integer) provided in format either {domain:bus:device:function} or "
        "{bus:device:function}, e.g. '0000:18:00.0', '18:00.0'",
    )
    interface_name: str | None = Field(None, description="Name of interface, e.g. 'eth3', 'Ethernet 5'")
    pci_device: str | None = Field(
        None,
        description="PCI Device (hexadecimal) provided in format {vid:did} or {vid:did:subvid:subdid}, "
        "e.g. '8086:1563', '8086:1563:0000:001A'",
    )
    interface_index: int | None = Field(None, description="Interface index - list index value.")
    interface_indexes: list[int] | None = Field(None, description="Interface indexes - list of index value.")
    family: str | None = Field(
        None, description="Family of network interfaces. Allow list is in DEVICE_IDS (mfd-consts)."
    )
    speed: str | None = Field(None, description="Speed of network interfaces. Allow list is in SPEED_IDS (mfd-consts).")
    random_interface: bool | None = Field(
        None,
        description="Return random interface for provided identifier: pci_device, interface_index, family or speed. "
        "Possible value: true",
    )
    all_interfaces: bool | None = Field(
        None,
        description="Return all interface for provided identifier: pci_device, interface_index, family or speed. "
        "Possible value: true",
    )
    ips: list[IPModel] | None = None
    switch_name: str | None = Field(
        None,
        description="Name of the switch which should be same as in switches section for getting all switch connection "
        "details.",
    )
    switch_port: str | None = Field(
        None,
        description="Name of the switch port to which the interface is connected on the switch (switch_name).",
    )
    vlan: str | None = Field(None, description="VLAN configured on Switch port")
    mac_address: str | None = Field(None, description="MAC address of the interface in format XX:XX:XX:XX:XX:XX")


class SUTModelBase(MachineModel):
    """SUT model."""

    role: Literal["sut", "client"]  # noqa: F821
    network_interfaces: list[NetworkInterfaceModelBase] | None = None
    connections: list[ConnectionModelBase] | None = None
    machine_type: Literal["regular", "ipu"] = "regular"  # noqa: F821
    ipu_host_type: IPUHostType | None = None

    @staticmethod
    def sort_function(v: ConnectionModelBase) -> int:
        """
        Sort connection model.

        Connections with relative model id should be placed in further position than normal connections.

        :param v: Connection model
        :return: Value for sort process
        """
        calculations = 0 if not v.relative_connection_id else v.relative_connection_id * 100
        calculations += v.connection_id
        return calculations


class ExtraInfoModel(BaseModel, extra="allow"):
    """Model for extra information."""

    suffix: str | None = None  # suffix to avoid duplication across different systems
    datastore: list[str] | None = None  # list of available datastore names to be used for VMs

    @field_validator("suffix", mode="before")
    @classmethod
    def validate_suffix_format(cls: ExtraInfoModel, v: str) -> str:
        """Validate PCI Device format."""
        if v and not isinstance(v, str):
            raise ValueError("Suffix must be provided in string format")
        return v

    @field_validator("datastore", mode="before")
    @classmethod
    def validate_datastore_format(cls: ExtraInfoModel, v: tuple[str, ...]) -> tuple[str, ...]:
        """Validate PCI Device format."""
        if v:
            for store in v:
                if not isinstance(store, str):
                    raise ValueError(f"Datastore name {store} be provided in string format.")
        return v


class HostModel(SUTModelBase, extra="forbid"):
    """Server model."""

    extra_info: ExtraInfoModel | None = None


class VMModel(SUTModelBase):
    """VM Model."""

    hypervisor: str = Field(None, description="Name of the VM's hypervisor")


class ContainerModel(SUTModelBase):
    """Container model."""


class SimicsSimulationModel(SUTModelBase):  # TODO: how to reflect simics simulation within the model
    """Simics simulation model."""


class ServiceModel(InstantiateBaseModel):
    """Service model."""

    type: Literal["vcsa", "nsx", "dhcp"]  # noqa: A003 F821
    username: str = None
    password: SecretStr = None
    ip_address: IPvAnyAddress = None
    label: str | None = None


class TopologyModelBase(BaseModel, extra="forbid"):
    """Topology model.

    Part of the infrastructure used for sake of test execution.
    One shall assume test framework has exclusive access to all the assets - meaning they should be reserved
    in Resource Manager prior to test execution
    """

    metadata: SchemaMetadata
    switches: list[SwitchModelBase] | None = None
    services: list[ServiceModel] | None = None
    hosts: list[HostModel] | None = None
    vms: list[VMModel] | None = None
    containers: list[ContainerModel] | None = None


class HostPairConnectionModel(BaseModel, extra="forbid"):
    """Host Pair Model."""

    bidirectional: bool
    hosts: list[str]

    @field_validator("hosts")
    @classmethod
    def check_hosts_length(cls: HostPairConnectionModel, v: list[str]) -> list[str]:
        """Check hosts length."""
        if len(v) != 2:
            raise ValueError(f"Hosts key must be exact 2-element long. Got: {v}")
        return v


class SecretModel(BaseModel, extra="forbid"):
    """Secret Model."""

    name: str
    value: SecretStr
