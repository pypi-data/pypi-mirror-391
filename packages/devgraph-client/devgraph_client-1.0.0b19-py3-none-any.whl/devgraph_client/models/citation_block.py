from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.citation_block_additional_location_info import CitationBlockAdditionalLocationInfo
    from ..models.image_block import ImageBlock
    from ..models.text_block import TextBlock


T = TypeVar("T", bound="CitationBlock")


@_attrs_define
class CitationBlock:
    """A representation of cited content from past messages.

    Attributes:
        cited_content (ImageBlock | TextBlock):
        source (str):
        title (str):
        additional_location_info (CitationBlockAdditionalLocationInfo):
        block_type (Literal['citation'] | Unset):  Default: 'citation'.
    """

    cited_content: ImageBlock | TextBlock
    source: str
    title: str
    additional_location_info: CitationBlockAdditionalLocationInfo
    block_type: Literal["citation"] | Unset = "citation"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.text_block import TextBlock

        cited_content: dict[str, Any]
        if isinstance(self.cited_content, TextBlock):
            cited_content = self.cited_content.to_dict()
        else:
            cited_content = self.cited_content.to_dict()

        source = self.source

        title = self.title

        additional_location_info = self.additional_location_info.to_dict()

        block_type = self.block_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cited_content": cited_content,
                "source": source,
                "title": title,
                "additional_location_info": additional_location_info,
            }
        )
        if block_type is not UNSET:
            field_dict["block_type"] = block_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.citation_block_additional_location_info import CitationBlockAdditionalLocationInfo
        from ..models.image_block import ImageBlock
        from ..models.text_block import TextBlock

        d = dict(src_dict)

        def _parse_cited_content(data: object) -> ImageBlock | TextBlock:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                cited_content_type_0 = TextBlock.from_dict(data)

                return cited_content_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            cited_content_type_1 = ImageBlock.from_dict(data)

            return cited_content_type_1

        cited_content = _parse_cited_content(d.pop("cited_content"))

        source = d.pop("source")

        title = d.pop("title")

        additional_location_info = CitationBlockAdditionalLocationInfo.from_dict(d.pop("additional_location_info"))

        block_type = cast(Literal["citation"] | Unset, d.pop("block_type", UNSET))
        if block_type != "citation" and not isinstance(block_type, Unset):
            raise ValueError(f"block_type must match const 'citation', got '{block_type}'")

        citation_block = cls(
            cited_content=cited_content,
            source=source,
            title=title,
            additional_location_info=additional_location_info,
            block_type=block_type,
        )

        citation_block.additional_properties = d
        return citation_block

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
