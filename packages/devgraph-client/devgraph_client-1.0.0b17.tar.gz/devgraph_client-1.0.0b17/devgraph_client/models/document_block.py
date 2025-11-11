from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="DocumentBlock")


@_attrs_define
class DocumentBlock:
    """A representation of a document to directly pass to the LLM.

    Attributes:
        block_type (Literal['document'] | Unset):  Default: 'document'.
        data (File | None | Unset):
        path (None | str | Unset):
        url (None | str | Unset):
        title (None | str | Unset):
        document_mimetype (None | str | Unset):
    """

    block_type: Literal["document"] | Unset = "document"
    data: File | None | Unset = UNSET
    path: None | str | Unset = UNSET
    url: None | str | Unset = UNSET
    title: None | str | Unset = UNSET
    document_mimetype: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        block_type = self.block_type

        data: FileTypes | None | Unset
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, File):
            data = self.data.to_tuple()

        else:
            data = self.data

        path: None | str | Unset
        if isinstance(self.path, Unset):
            path = UNSET
        else:
            path = self.path

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        document_mimetype: None | str | Unset
        if isinstance(self.document_mimetype, Unset):
            document_mimetype = UNSET
        else:
            document_mimetype = self.document_mimetype

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if block_type is not UNSET:
            field_dict["block_type"] = block_type
        if data is not UNSET:
            field_dict["data"] = data
        if path is not UNSET:
            field_dict["path"] = path
        if url is not UNSET:
            field_dict["url"] = url
        if title is not UNSET:
            field_dict["title"] = title
        if document_mimetype is not UNSET:
            field_dict["document_mimetype"] = document_mimetype

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        block_type = cast(Literal["document"] | Unset, d.pop("block_type", UNSET))
        if block_type != "document" and not isinstance(block_type, Unset):
            raise ValueError(f"block_type must match const 'document', got '{block_type}'")

        def _parse_data(data: object) -> File | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                data_type_0 = File(payload=BytesIO(data))

                return data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(File | None | Unset, data)

        data = _parse_data(d.pop("data", UNSET))

        def _parse_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        path = _parse_path(d.pop("path", UNSET))

        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_document_mimetype(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        document_mimetype = _parse_document_mimetype(d.pop("document_mimetype", UNSET))

        document_block = cls(
            block_type=block_type,
            data=data,
            path=path,
            url=url,
            title=title,
            document_mimetype=document_mimetype,
        )

        document_block.additional_properties = d
        return document_block

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
