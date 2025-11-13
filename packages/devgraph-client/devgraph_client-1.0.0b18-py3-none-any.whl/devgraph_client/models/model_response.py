from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelResponse")


@_attrs_define
class ModelResponse:
    """
    Attributes:
        id (UUID):
        name (str):
        provider_id (UUID):
        description (None | str | Unset):
        default (bool | Unset):  Default: False.
    """

    id: UUID
    name: str
    provider_id: UUID
    description: None | str | Unset = UNSET
    default: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        provider_id = str(self.provider_id)

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        default = self.default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "provider_id": provider_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if default is not UNSET:
            field_dict["default"] = default

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        provider_id = UUID(d.pop("provider_id"))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        default = d.pop("default", UNSET)

        model_response = cls(
            id=id,
            name=name,
            provider_id=provider_id,
            description=description,
            default=default,
        )

        model_response.additional_properties = d
        return model_response

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
