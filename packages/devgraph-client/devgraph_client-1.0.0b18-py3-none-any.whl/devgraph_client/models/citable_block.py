from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_block import DocumentBlock
    from ..models.image_block import ImageBlock
    from ..models.text_block import TextBlock


T = TypeVar("T", bound="CitableBlock")


@_attrs_define
class CitableBlock:
    """Supports providing citable content to LLMs that have built-in citation support.

    Attributes:
        title (str):
        source (str):
        content (list[DocumentBlock | ImageBlock | TextBlock]):
        block_type (Literal['citable'] | Unset):  Default: 'citable'.
    """

    title: str
    source: str
    content: list[DocumentBlock | ImageBlock | TextBlock]
    block_type: Literal["citable"] | Unset = "citable"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.image_block import ImageBlock
        from ..models.text_block import TextBlock

        title = self.title

        source = self.source

        content = []
        for content_item_data in self.content:
            content_item: dict[str, Any]
            if isinstance(content_item_data, TextBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, ImageBlock):
                content_item = content_item_data.to_dict()
            else:
                content_item = content_item_data.to_dict()

            content.append(content_item)

        block_type = self.block_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "source": source,
                "content": content,
            }
        )
        if block_type is not UNSET:
            field_dict["block_type"] = block_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_block import DocumentBlock
        from ..models.image_block import ImageBlock
        from ..models.text_block import TextBlock

        d = dict(src_dict)
        title = d.pop("title")

        source = d.pop("source")

        content = []
        _content = d.pop("content")
        for content_item_data in _content:

            def _parse_content_item(data: object) -> DocumentBlock | ImageBlock | TextBlock:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_0 = TextBlock.from_dict(data)

                    return content_item_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_1 = ImageBlock.from_dict(data)

                    return content_item_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                content_item_type_2 = DocumentBlock.from_dict(data)

                return content_item_type_2

            content_item = _parse_content_item(content_item_data)

            content.append(content_item)

        block_type = cast(Literal["citable"] | Unset, d.pop("block_type", UNSET))
        if block_type != "citable" and not isinstance(block_type, Unset):
            raise ValueError(f"block_type must match const 'citable', got '{block_type}'")

        citable_block = cls(
            title=title,
            source=source,
            content=content,
            block_type=block_type,
        )

        citable_block.additional_properties = d
        return citable_block

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
