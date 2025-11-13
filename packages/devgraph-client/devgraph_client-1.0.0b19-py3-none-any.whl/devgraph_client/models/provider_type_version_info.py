from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.provider_version_info import ProviderVersionInfo


T = TypeVar("T", bound="ProviderTypeVersionInfo")


@_attrs_define
class ProviderTypeVersionInfo:
    """Version information for a provider type.

    Attributes:
        provider_type (str):
        current_version (int):
        supported_versions (list[ProviderVersionInfo]):
    """

    provider_type: str
    current_version: int
    supported_versions: list[ProviderVersionInfo]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider_type = self.provider_type

        current_version = self.current_version

        supported_versions = []
        for supported_versions_item_data in self.supported_versions:
            supported_versions_item = supported_versions_item_data.to_dict()
            supported_versions.append(supported_versions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider_type": provider_type,
                "current_version": current_version,
                "supported_versions": supported_versions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provider_version_info import ProviderVersionInfo

        d = dict(src_dict)
        provider_type = d.pop("provider_type")

        current_version = d.pop("current_version")

        supported_versions = []
        _supported_versions = d.pop("supported_versions")
        for supported_versions_item_data in _supported_versions:
            supported_versions_item = ProviderVersionInfo.from_dict(supported_versions_item_data)

            supported_versions.append(supported_versions_item)

        provider_type_version_info = cls(
            provider_type=provider_type,
            current_version=current_version,
            supported_versions=supported_versions,
        )

        provider_type_version_info.additional_properties = d
        return provider_type_version_info

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
