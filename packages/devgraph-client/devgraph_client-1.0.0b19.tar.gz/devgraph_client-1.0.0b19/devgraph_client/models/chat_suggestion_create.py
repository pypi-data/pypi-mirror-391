from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChatSuggestionCreate")


@_attrs_define
class ChatSuggestionCreate:
    """
    Attributes:
        title (str):
        label (str):
        action (str):
        active (bool | Unset):  Default: True.
    """

    title: str
    label: str
    action: str
    active: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        label = self.label

        action = self.action

        active = self.active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "label": label,
                "action": action,
            }
        )
        if active is not UNSET:
            field_dict["active"] = active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        label = d.pop("label")

        action = d.pop("action")

        active = d.pop("active", UNSET)

        chat_suggestion_create = cls(
            title=title,
            label=label,
            action=action,
            active=active,
        )

        chat_suggestion_create.additional_properties = d
        return chat_suggestion_create

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
