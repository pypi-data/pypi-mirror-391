from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MigrationResult")


@_attrs_define
class MigrationResult:
    """Result of a config migration.

    Attributes:
        provider_id (UUID):
        success (bool):
        old_version (int):
        new_version (int | None | Unset):
        error (None | str | Unset):
    """

    provider_id: UUID
    success: bool
    old_version: int
    new_version: int | None | Unset = UNSET
    error: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider_id = str(self.provider_id)

        success = self.success

        old_version = self.old_version

        new_version: int | None | Unset
        if isinstance(self.new_version, Unset):
            new_version = UNSET
        else:
            new_version = self.new_version

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider_id": provider_id,
                "success": success,
                "old_version": old_version,
            }
        )
        if new_version is not UNSET:
            field_dict["new_version"] = new_version
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        provider_id = UUID(d.pop("provider_id"))

        success = d.pop("success")

        old_version = d.pop("old_version")

        def _parse_new_version(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        new_version = _parse_new_version(d.pop("new_version", UNSET))

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        migration_result = cls(
            provider_id=provider_id,
            success=success,
            old_version=old_version,
            new_version=new_version,
            error=error,
        )

        migration_result.additional_properties = d
        return migration_result

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
