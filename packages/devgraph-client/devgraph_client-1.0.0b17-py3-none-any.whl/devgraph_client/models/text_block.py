from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TextBlock")


@_attrs_define
class TextBlock:
    """A representation of text data to directly pass to/from the LLM.

    Attributes:
        text (str):
        block_type (Literal['text'] | Unset):  Default: 'text'.
    """

    text: str
    block_type: Literal["text"] | Unset = "text"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        block_type = self.block_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "text": text,
            }
        )
        if block_type is not UNSET:
            field_dict["block_type"] = block_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        text = d.pop("text")

        block_type = cast(Literal["text"] | Unset, d.pop("block_type", UNSET))
        if block_type != "text" and not isinstance(block_type, Unset):
            raise ValueError(f"block_type must match const 'text', got '{block_type}'")

        text_block = cls(
            text=text,
            block_type=block_type,
        )

        text_block.additional_properties = d
        return text_block

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
