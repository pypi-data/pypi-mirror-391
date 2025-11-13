from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProviderVersionInfo")


@_attrs_define
class ProviderVersionInfo:
    """Information about a provider config version.

    Attributes:
        version (int):
        current (bool):
        deprecated (bool):
        deprecated_at (None | str | Unset):
        removal_at (None | str | Unset):
        deprecation_message (None | str | Unset):
        days_until_removal (int | None | Unset):
    """

    version: int
    current: bool
    deprecated: bool
    deprecated_at: None | str | Unset = UNSET
    removal_at: None | str | Unset = UNSET
    deprecation_message: None | str | Unset = UNSET
    days_until_removal: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        current = self.current

        deprecated = self.deprecated

        deprecated_at: None | str | Unset
        if isinstance(self.deprecated_at, Unset):
            deprecated_at = UNSET
        else:
            deprecated_at = self.deprecated_at

        removal_at: None | str | Unset
        if isinstance(self.removal_at, Unset):
            removal_at = UNSET
        else:
            removal_at = self.removal_at

        deprecation_message: None | str | Unset
        if isinstance(self.deprecation_message, Unset):
            deprecation_message = UNSET
        else:
            deprecation_message = self.deprecation_message

        days_until_removal: int | None | Unset
        if isinstance(self.days_until_removal, Unset):
            days_until_removal = UNSET
        else:
            days_until_removal = self.days_until_removal

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
                "current": current,
                "deprecated": deprecated,
            }
        )
        if deprecated_at is not UNSET:
            field_dict["deprecated_at"] = deprecated_at
        if removal_at is not UNSET:
            field_dict["removal_at"] = removal_at
        if deprecation_message is not UNSET:
            field_dict["deprecation_message"] = deprecation_message
        if days_until_removal is not UNSET:
            field_dict["days_until_removal"] = days_until_removal

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        version = d.pop("version")

        current = d.pop("current")

        deprecated = d.pop("deprecated")

        def _parse_deprecated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deprecated_at = _parse_deprecated_at(d.pop("deprecated_at", UNSET))

        def _parse_removal_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        removal_at = _parse_removal_at(d.pop("removal_at", UNSET))

        def _parse_deprecation_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deprecation_message = _parse_deprecation_message(d.pop("deprecation_message", UNSET))

        def _parse_days_until_removal(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        days_until_removal = _parse_days_until_removal(d.pop("days_until_removal", UNSET))

        provider_version_info = cls(
            version=version,
            current=current,
            deprecated=deprecated,
            deprecated_at=deprecated_at,
            removal_at=removal_at,
            deprecation_message=deprecation_message,
            days_until_removal=days_until_removal,
        )

        provider_version_info.additional_properties = d
        return provider_version_info

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
