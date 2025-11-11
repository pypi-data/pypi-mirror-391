from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PromptResponse")


@_attrs_define
class PromptResponse:
    """
    Attributes:
        id (UUID):
        name (str):
        content (str):
        environment_id (UUID):
        created_at (str):
        updated_at (str):
        description (None | str | Unset):
        active (bool | Unset):  Default: True.
        is_default (bool | Unset):  Default: False.
    """

    id: UUID
    name: str
    content: str
    environment_id: UUID
    created_at: str
    updated_at: str
    description: None | str | Unset = UNSET
    active: bool | Unset = True
    is_default: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        content = self.content

        environment_id = str(self.environment_id)

        created_at = self.created_at

        updated_at = self.updated_at

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        active = self.active

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "content": content,
                "environment_id": environment_id,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if active is not UNSET:
            field_dict["active"] = active
        if is_default is not UNSET:
            field_dict["is_default"] = is_default

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        content = d.pop("content")

        environment_id = UUID(d.pop("environment_id"))

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        active = d.pop("active", UNSET)

        is_default = d.pop("is_default", UNSET)

        prompt_response = cls(
            id=id,
            name=name,
            content=content,
            environment_id=environment_id,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            active=active,
            is_default=is_default,
        )

        prompt_response.additional_properties = d
        return prompt_response

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
