from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="ImageBlock")


@_attrs_define
class ImageBlock:
    """A representation of image data to directly pass to/from the LLM.

    Attributes:
        block_type (Literal['image'] | Unset):  Default: 'image'.
        image (File | None | Unset):
        path (None | str | Unset):
        url (None | str | Unset):
        image_mimetype (None | str | Unset):
        detail (None | str | Unset):
    """

    block_type: Literal["image"] | Unset = "image"
    image: File | None | Unset = UNSET
    path: None | str | Unset = UNSET
    url: None | str | Unset = UNSET
    image_mimetype: None | str | Unset = UNSET
    detail: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        block_type = self.block_type

        image: FileTypes | None | Unset
        if isinstance(self.image, Unset):
            image = UNSET
        elif isinstance(self.image, File):
            image = self.image.to_tuple()

        else:
            image = self.image

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

        image_mimetype: None | str | Unset
        if isinstance(self.image_mimetype, Unset):
            image_mimetype = UNSET
        else:
            image_mimetype = self.image_mimetype

        detail: None | str | Unset
        if isinstance(self.detail, Unset):
            detail = UNSET
        else:
            detail = self.detail

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if block_type is not UNSET:
            field_dict["block_type"] = block_type
        if image is not UNSET:
            field_dict["image"] = image
        if path is not UNSET:
            field_dict["path"] = path
        if url is not UNSET:
            field_dict["url"] = url
        if image_mimetype is not UNSET:
            field_dict["image_mimetype"] = image_mimetype
        if detail is not UNSET:
            field_dict["detail"] = detail

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        block_type = cast(Literal["image"] | Unset, d.pop("block_type", UNSET))
        if block_type != "image" and not isinstance(block_type, Unset):
            raise ValueError(f"block_type must match const 'image', got '{block_type}'")

        def _parse_image(data: object) -> File | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                image_type_0 = File(payload=BytesIO(data))

                return image_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(File | None | Unset, data)

        image = _parse_image(d.pop("image", UNSET))

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

        def _parse_image_mimetype(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        image_mimetype = _parse_image_mimetype(d.pop("image_mimetype", UNSET))

        def _parse_detail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        detail = _parse_detail(d.pop("detail", UNSET))

        image_block = cls(
            block_type=block_type,
            image=image,
            path=path,
            url=url,
            image_mimetype=image_mimetype,
            detail=detail,
        )

        image_block.additional_properties = d
        return image_block

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
