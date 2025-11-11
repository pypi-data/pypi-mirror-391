from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.configured_provider_create_config import ConfiguredProviderCreateConfig


T = TypeVar("T", bound="ConfiguredProviderCreate")


@_attrs_define
class ConfiguredProviderCreate:
    """Request to create a configured discovery provider.

    Attributes:
        name (str): Human-readable name for this provider instance
        provider_type (str): Type of provider (github, gitlab, etc.)
        config (ConfiguredProviderCreateConfig): Provider configuration (will be encrypted)
        enabled (bool | Unset): Whether this provider is active Default: True.
        interval (int | Unset): Discovery interval in seconds (minimum 60) Default: 300.
    """

    name: str
    provider_type: str
    config: ConfiguredProviderCreateConfig
    enabled: bool | Unset = True
    interval: int | Unset = 300
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        provider_type = self.provider_type

        config = self.config.to_dict()

        enabled = self.enabled

        interval = self.interval

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "provider_type": provider_type,
                "config": config,
            }
        )
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if interval is not UNSET:
            field_dict["interval"] = interval

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.configured_provider_create_config import ConfiguredProviderCreateConfig

        d = dict(src_dict)
        name = d.pop("name")

        provider_type = d.pop("provider_type")

        config = ConfiguredProviderCreateConfig.from_dict(d.pop("config"))

        enabled = d.pop("enabled", UNSET)

        interval = d.pop("interval", UNSET)

        configured_provider_create = cls(
            name=name,
            provider_type=provider_type,
            config=config,
            enabled=enabled,
            interval=interval,
        )

        configured_provider_create.additional_properties = d
        return configured_provider_create

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
