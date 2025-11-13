from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChatSuggestionResponse")


@_attrs_define
class ChatSuggestionResponse:
    """
    Attributes:
        id (UUID):
        title (str):
        label (str):
        action (str):
        created_at (str):
        updated_at (str):
        active (bool | Unset):  Default: True.
        is_system (bool | Unset):  Default: False.
        environment_id (None | Unset | UUID):
    """

    id: UUID
    title: str
    label: str
    action: str
    created_at: str
    updated_at: str
    active: bool | Unset = True
    is_system: bool | Unset = False
    environment_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        title = self.title

        label = self.label

        action = self.action

        created_at = self.created_at

        updated_at = self.updated_at

        active = self.active

        is_system = self.is_system

        environment_id: None | str | Unset
        if isinstance(self.environment_id, Unset):
            environment_id = UNSET
        elif isinstance(self.environment_id, UUID):
            environment_id = str(self.environment_id)
        else:
            environment_id = self.environment_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
                "label": label,
                "action": action,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if active is not UNSET:
            field_dict["active"] = active
        if is_system is not UNSET:
            field_dict["is_system"] = is_system
        if environment_id is not UNSET:
            field_dict["environment_id"] = environment_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        title = d.pop("title")

        label = d.pop("label")

        action = d.pop("action")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        active = d.pop("active", UNSET)

        is_system = d.pop("is_system", UNSET)

        def _parse_environment_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                environment_id_type_0 = UUID(data)

                return environment_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        environment_id = _parse_environment_id(d.pop("environment_id", UNSET))

        chat_suggestion_response = cls(
            id=id,
            title=title,
            label=label,
            action=action,
            created_at=created_at,
            updated_at=updated_at,
            active=active,
            is_system=is_system,
            environment_id=environment_id,
        )

        chat_suggestion_response.additional_properties = d
        return chat_suggestion_response

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
