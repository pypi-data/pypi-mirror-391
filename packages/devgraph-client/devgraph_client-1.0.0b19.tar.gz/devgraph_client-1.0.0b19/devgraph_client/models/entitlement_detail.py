from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitlementDetail")


@_attrs_define
class EntitlementDetail:
    """
    Attributes:
        limit_value (int | None | Unset):
        enabled (bool | None | Unset):
        config_value (None | str | Unset):
        current_usage (int | None | Unset):
        remaining (int | None | Unset):
    """

    limit_value: int | None | Unset = UNSET
    enabled: bool | None | Unset = UNSET
    config_value: None | str | Unset = UNSET
    current_usage: int | None | Unset = UNSET
    remaining: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit_value: int | None | Unset
        if isinstance(self.limit_value, Unset):
            limit_value = UNSET
        else:
            limit_value = self.limit_value

        enabled: bool | None | Unset
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        config_value: None | str | Unset
        if isinstance(self.config_value, Unset):
            config_value = UNSET
        else:
            config_value = self.config_value

        current_usage: int | None | Unset
        if isinstance(self.current_usage, Unset):
            current_usage = UNSET
        else:
            current_usage = self.current_usage

        remaining: int | None | Unset
        if isinstance(self.remaining, Unset):
            remaining = UNSET
        else:
            remaining = self.remaining

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if limit_value is not UNSET:
            field_dict["limit_value"] = limit_value
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if config_value is not UNSET:
            field_dict["config_value"] = config_value
        if current_usage is not UNSET:
            field_dict["current_usage"] = current_usage
        if remaining is not UNSET:
            field_dict["remaining"] = remaining

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_limit_value(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        limit_value = _parse_limit_value(d.pop("limit_value", UNSET))

        def _parse_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        def _parse_config_value(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        config_value = _parse_config_value(d.pop("config_value", UNSET))

        def _parse_current_usage(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        current_usage = _parse_current_usage(d.pop("current_usage", UNSET))

        def _parse_remaining(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        remaining = _parse_remaining(d.pop("remaining", UNSET))

        entitlement_detail = cls(
            limit_value=limit_value,
            enabled=enabled,
            config_value=config_value,
            current_usage=current_usage,
            remaining=remaining,
        )

        entitlement_detail.additional_properties = d
        return entitlement_detail

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
