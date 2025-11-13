from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.configured_provider_update_config_type_0 import ConfiguredProviderUpdateConfigType0


T = TypeVar("T", bound="ConfiguredProviderUpdate")


@_attrs_define
class ConfiguredProviderUpdate:
    """Request to update a configured discovery provider.

    Attributes:
        name (None | str | Unset):
        enabled (bool | None | Unset):
        interval (int | None | Unset):
        config (ConfiguredProviderUpdateConfigType0 | None | Unset):
    """

    name: None | str | Unset = UNSET
    enabled: bool | None | Unset = UNSET
    interval: int | None | Unset = UNSET
    config: ConfiguredProviderUpdateConfigType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.configured_provider_update_config_type_0 import ConfiguredProviderUpdateConfigType0

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        enabled: bool | None | Unset
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        interval: int | None | Unset
        if isinstance(self.interval, Unset):
            interval = UNSET
        else:
            interval = self.interval

        config: dict[str, Any] | None | Unset
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, ConfiguredProviderUpdateConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if interval is not UNSET:
            field_dict["interval"] = interval
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.configured_provider_update_config_type_0 import ConfiguredProviderUpdateConfigType0

        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        def _parse_interval(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        interval = _parse_interval(d.pop("interval", UNSET))

        def _parse_config(data: object) -> ConfiguredProviderUpdateConfigType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = ConfiguredProviderUpdateConfigType0.from_dict(data)

                return config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ConfiguredProviderUpdateConfigType0 | None | Unset, data)

        config = _parse_config(d.pop("config", UNSET))

        configured_provider_update = cls(
            name=name,
            enabled=enabled,
            interval=interval,
            config=config,
        )

        configured_provider_update.additional_properties = d
        return configured_provider_update

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
