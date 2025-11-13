from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.thinking_block_additional_information import ThinkingBlockAdditionalInformation


T = TypeVar("T", bound="ThinkingBlock")


@_attrs_define
class ThinkingBlock:
    """A representation of the content streamed from reasoning/thinking processes by LLMs

    Attributes:
        block_type (Literal['thinking'] | Unset):  Default: 'thinking'.
        content (None | str | Unset):
        num_tokens (int | None | Unset):
        additional_information (ThinkingBlockAdditionalInformation | Unset): Additional information related to the
            thinking/reasoning process, if available
    """

    block_type: Literal["thinking"] | Unset = "thinking"
    content: None | str | Unset = UNSET
    num_tokens: int | None | Unset = UNSET
    additional_information: ThinkingBlockAdditionalInformation | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        block_type = self.block_type

        content: None | str | Unset
        if isinstance(self.content, Unset):
            content = UNSET
        else:
            content = self.content

        num_tokens: int | None | Unset
        if isinstance(self.num_tokens, Unset):
            num_tokens = UNSET
        else:
            num_tokens = self.num_tokens

        additional_information: dict[str, Any] | Unset = UNSET
        if not isinstance(self.additional_information, Unset):
            additional_information = self.additional_information.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if block_type is not UNSET:
            field_dict["block_type"] = block_type
        if content is not UNSET:
            field_dict["content"] = content
        if num_tokens is not UNSET:
            field_dict["num_tokens"] = num_tokens
        if additional_information is not UNSET:
            field_dict["additional_information"] = additional_information

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.thinking_block_additional_information import ThinkingBlockAdditionalInformation

        d = dict(src_dict)
        block_type = cast(Literal["thinking"] | Unset, d.pop("block_type", UNSET))
        if block_type != "thinking" and not isinstance(block_type, Unset):
            raise ValueError(f"block_type must match const 'thinking', got '{block_type}'")

        def _parse_content(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        content = _parse_content(d.pop("content", UNSET))

        def _parse_num_tokens(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        num_tokens = _parse_num_tokens(d.pop("num_tokens", UNSET))

        _additional_information = d.pop("additional_information", UNSET)
        additional_information: ThinkingBlockAdditionalInformation | Unset
        if isinstance(_additional_information, Unset):
            additional_information = UNSET
        else:
            additional_information = ThinkingBlockAdditionalInformation.from_dict(_additional_information)

        thinking_block = cls(
            block_type=block_type,
            content=content,
            num_tokens=num_tokens,
            additional_information=additional_information,
        )

        thinking_block.additional_properties = d
        return thinking_block

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
