from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="AudioBlock")


@_attrs_define
class AudioBlock:
    """A representation of audio data to directly pass to/from the LLM.

    Attributes:
        block_type (Literal['audio'] | Unset):  Default: 'audio'.
        audio (File | None | Unset):
        path (None | str | Unset):
        url (None | str | Unset):
        format_ (None | str | Unset):
    """

    block_type: Literal["audio"] | Unset = "audio"
    audio: File | None | Unset = UNSET
    path: None | str | Unset = UNSET
    url: None | str | Unset = UNSET
    format_: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        block_type = self.block_type

        audio: FileTypes | None | Unset
        if isinstance(self.audio, Unset):
            audio = UNSET
        elif isinstance(self.audio, File):
            audio = self.audio.to_tuple()

        else:
            audio = self.audio

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

        format_: None | str | Unset
        if isinstance(self.format_, Unset):
            format_ = UNSET
        else:
            format_ = self.format_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if block_type is not UNSET:
            field_dict["block_type"] = block_type
        if audio is not UNSET:
            field_dict["audio"] = audio
        if path is not UNSET:
            field_dict["path"] = path
        if url is not UNSET:
            field_dict["url"] = url
        if format_ is not UNSET:
            field_dict["format"] = format_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        block_type = cast(Literal["audio"] | Unset, d.pop("block_type", UNSET))
        if block_type != "audio" and not isinstance(block_type, Unset):
            raise ValueError(f"block_type must match const 'audio', got '{block_type}'")

        def _parse_audio(data: object) -> File | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                audio_type_0 = File(payload=BytesIO(data))

                return audio_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(File | None | Unset, data)

        audio = _parse_audio(d.pop("audio", UNSET))

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

        def _parse_format_(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        format_ = _parse_format_(d.pop("format", UNSET))

        audio_block = cls(
            block_type=block_type,
            audio=audio,
            path=path,
            url=url,
            format_=format_,
        )

        audio_block.additional_properties = d
        return audio_block

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
