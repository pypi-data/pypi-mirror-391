from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.message_role import MessageRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.audio_block import AudioBlock
    from ..models.cache_point import CachePoint
    from ..models.chat_message_additional_kwargs import ChatMessageAdditionalKwargs
    from ..models.citable_block import CitableBlock
    from ..models.citation_block import CitationBlock
    from ..models.document_block import DocumentBlock
    from ..models.image_block import ImageBlock
    from ..models.text_block import TextBlock
    from ..models.thinking_block import ThinkingBlock
    from ..models.tool_call_block import ToolCallBlock
    from ..models.video_block import VideoBlock


T = TypeVar("T", bound="ChatMessage")


@_attrs_define
class ChatMessage:
    """Chat message.

    Attributes:
        role (MessageRole | Unset): Message role.
        additional_kwargs (ChatMessageAdditionalKwargs | Unset):
        blocks (list[AudioBlock | CachePoint | CitableBlock | CitationBlock | DocumentBlock | ImageBlock | TextBlock |
            ThinkingBlock | ToolCallBlock | VideoBlock] | Unset):
    """

    role: MessageRole | Unset = UNSET
    additional_kwargs: ChatMessageAdditionalKwargs | Unset = UNSET
    blocks: (
        list[
            AudioBlock
            | CachePoint
            | CitableBlock
            | CitationBlock
            | DocumentBlock
            | ImageBlock
            | TextBlock
            | ThinkingBlock
            | ToolCallBlock
            | VideoBlock
        ]
        | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.audio_block import AudioBlock
        from ..models.cache_point import CachePoint
        from ..models.citable_block import CitableBlock
        from ..models.citation_block import CitationBlock
        from ..models.document_block import DocumentBlock
        from ..models.image_block import ImageBlock
        from ..models.text_block import TextBlock
        from ..models.thinking_block import ThinkingBlock
        from ..models.video_block import VideoBlock

        role: str | Unset = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        additional_kwargs: dict[str, Any] | Unset = UNSET
        if not isinstance(self.additional_kwargs, Unset):
            additional_kwargs = self.additional_kwargs.to_dict()

        blocks: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.blocks, Unset):
            blocks = []
            for blocks_item_data in self.blocks:
                blocks_item: dict[str, Any]
                if isinstance(blocks_item_data, TextBlock):
                    blocks_item = blocks_item_data.to_dict()
                elif isinstance(blocks_item_data, ImageBlock):
                    blocks_item = blocks_item_data.to_dict()
                elif isinstance(blocks_item_data, AudioBlock):
                    blocks_item = blocks_item_data.to_dict()
                elif isinstance(blocks_item_data, VideoBlock):
                    blocks_item = blocks_item_data.to_dict()
                elif isinstance(blocks_item_data, DocumentBlock):
                    blocks_item = blocks_item_data.to_dict()
                elif isinstance(blocks_item_data, CachePoint):
                    blocks_item = blocks_item_data.to_dict()
                elif isinstance(blocks_item_data, CitableBlock):
                    blocks_item = blocks_item_data.to_dict()
                elif isinstance(blocks_item_data, CitationBlock):
                    blocks_item = blocks_item_data.to_dict()
                elif isinstance(blocks_item_data, ThinkingBlock):
                    blocks_item = blocks_item_data.to_dict()
                else:
                    blocks_item = blocks_item_data.to_dict()

                blocks.append(blocks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if role is not UNSET:
            field_dict["role"] = role
        if additional_kwargs is not UNSET:
            field_dict["additional_kwargs"] = additional_kwargs
        if blocks is not UNSET:
            field_dict["blocks"] = blocks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audio_block import AudioBlock
        from ..models.cache_point import CachePoint
        from ..models.chat_message_additional_kwargs import ChatMessageAdditionalKwargs
        from ..models.citable_block import CitableBlock
        from ..models.citation_block import CitationBlock
        from ..models.document_block import DocumentBlock
        from ..models.image_block import ImageBlock
        from ..models.text_block import TextBlock
        from ..models.thinking_block import ThinkingBlock
        from ..models.tool_call_block import ToolCallBlock
        from ..models.video_block import VideoBlock

        d = dict(src_dict)
        _role = d.pop("role", UNSET)
        role: MessageRole | Unset
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = MessageRole(_role)

        _additional_kwargs = d.pop("additional_kwargs", UNSET)
        additional_kwargs: ChatMessageAdditionalKwargs | Unset
        if isinstance(_additional_kwargs, Unset):
            additional_kwargs = UNSET
        else:
            additional_kwargs = ChatMessageAdditionalKwargs.from_dict(_additional_kwargs)

        _blocks = d.pop("blocks", UNSET)
        blocks: (
            list[
                AudioBlock
                | CachePoint
                | CitableBlock
                | CitationBlock
                | DocumentBlock
                | ImageBlock
                | TextBlock
                | ThinkingBlock
                | ToolCallBlock
                | VideoBlock
            ]
            | Unset
        ) = UNSET
        if _blocks is not UNSET:
            blocks = []
            for blocks_item_data in _blocks:

                def _parse_blocks_item(
                    data: object,
                ) -> (
                    AudioBlock
                    | CachePoint
                    | CitableBlock
                    | CitationBlock
                    | DocumentBlock
                    | ImageBlock
                    | TextBlock
                    | ThinkingBlock
                    | ToolCallBlock
                    | VideoBlock
                ):
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        blocks_item_type_0 = TextBlock.from_dict(data)

                        return blocks_item_type_0
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        blocks_item_type_1 = ImageBlock.from_dict(data)

                        return blocks_item_type_1
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        blocks_item_type_2 = AudioBlock.from_dict(data)

                        return blocks_item_type_2
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        blocks_item_type_3 = VideoBlock.from_dict(data)

                        return blocks_item_type_3
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        blocks_item_type_4 = DocumentBlock.from_dict(data)

                        return blocks_item_type_4
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        blocks_item_type_5 = CachePoint.from_dict(data)

                        return blocks_item_type_5
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        blocks_item_type_6 = CitableBlock.from_dict(data)

                        return blocks_item_type_6
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        blocks_item_type_7 = CitationBlock.from_dict(data)

                        return blocks_item_type_7
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        blocks_item_type_8 = ThinkingBlock.from_dict(data)

                        return blocks_item_type_8
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    if not isinstance(data, dict):
                        raise TypeError()
                    blocks_item_type_9 = ToolCallBlock.from_dict(data)

                    return blocks_item_type_9

                blocks_item = _parse_blocks_item(blocks_item_data)

                blocks.append(blocks_item)

        chat_message = cls(
            role=role,
            additional_kwargs=additional_kwargs,
            blocks=blocks,
        )

        chat_message.additional_properties = d
        return chat_message

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
