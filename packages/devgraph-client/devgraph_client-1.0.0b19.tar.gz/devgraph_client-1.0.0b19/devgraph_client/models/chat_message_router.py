from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.typed_chat_message_content import TypedChatMessageContent


T = TypeVar("T", bound="ChatMessageRouter")


@_attrs_define
class ChatMessageRouter:
    """
    Attributes:
        id (UUID):
        chat_id (UUID):
        role (str):
        content (list[TypedChatMessageContent] | str):
        created_at (datetime.datetime):
    """

    id: UUID
    chat_id: UUID
    role: str
    content: list[TypedChatMessageContent] | str
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        chat_id = str(self.chat_id)

        role = self.role

        content: list[dict[str, Any]] | str
        if isinstance(self.content, list):
            content = []
            for content_type_1_item_data in self.content:
                content_type_1_item = content_type_1_item_data.to_dict()
                content.append(content_type_1_item)

        else:
            content = self.content

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "chatId": chat_id,
                "role": role,
                "content": content,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.typed_chat_message_content import TypedChatMessageContent

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        chat_id = UUID(d.pop("chatId"))

        role = d.pop("role")

        def _parse_content(data: object) -> list[TypedChatMessageContent] | str:
            try:
                if not isinstance(data, list):
                    raise TypeError()
                content_type_1 = []
                _content_type_1 = data
                for content_type_1_item_data in _content_type_1:
                    content_type_1_item = TypedChatMessageContent.from_dict(content_type_1_item_data)

                    content_type_1.append(content_type_1_item)

                return content_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[TypedChatMessageContent] | str, data)

        content = _parse_content(d.pop("content"))

        created_at = isoparse(d.pop("createdAt"))

        chat_message_router = cls(
            id=id,
            chat_id=chat_id,
            role=role,
            content=content,
            created_at=created_at,
        )

        chat_message_router.additional_properties = d
        return chat_message_router

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
