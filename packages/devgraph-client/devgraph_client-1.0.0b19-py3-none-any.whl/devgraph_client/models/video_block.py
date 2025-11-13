from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="VideoBlock")


@_attrs_define
class VideoBlock:
    """A representation of video data to directly pass to/from the LLM.

    Attributes:
        block_type (Literal['video'] | Unset):  Default: 'video'.
        video (File | None | Unset):
        path (None | str | Unset):
        url (None | str | Unset):
        video_mimetype (None | str | Unset):
        detail (None | str | Unset):
        fps (int | None | Unset):
    """

    block_type: Literal["video"] | Unset = "video"
    video: File | None | Unset = UNSET
    path: None | str | Unset = UNSET
    url: None | str | Unset = UNSET
    video_mimetype: None | str | Unset = UNSET
    detail: None | str | Unset = UNSET
    fps: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        block_type = self.block_type

        video: FileTypes | None | Unset
        if isinstance(self.video, Unset):
            video = UNSET
        elif isinstance(self.video, File):
            video = self.video.to_tuple()

        else:
            video = self.video

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

        video_mimetype: None | str | Unset
        if isinstance(self.video_mimetype, Unset):
            video_mimetype = UNSET
        else:
            video_mimetype = self.video_mimetype

        detail: None | str | Unset
        if isinstance(self.detail, Unset):
            detail = UNSET
        else:
            detail = self.detail

        fps: int | None | Unset
        if isinstance(self.fps, Unset):
            fps = UNSET
        else:
            fps = self.fps

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if block_type is not UNSET:
            field_dict["block_type"] = block_type
        if video is not UNSET:
            field_dict["video"] = video
        if path is not UNSET:
            field_dict["path"] = path
        if url is not UNSET:
            field_dict["url"] = url
        if video_mimetype is not UNSET:
            field_dict["video_mimetype"] = video_mimetype
        if detail is not UNSET:
            field_dict["detail"] = detail
        if fps is not UNSET:
            field_dict["fps"] = fps

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        block_type = cast(Literal["video"] | Unset, d.pop("block_type", UNSET))
        if block_type != "video" and not isinstance(block_type, Unset):
            raise ValueError(f"block_type must match const 'video', got '{block_type}'")

        def _parse_video(data: object) -> File | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                video_type_0 = File(payload=BytesIO(data))

                return video_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(File | None | Unset, data)

        video = _parse_video(d.pop("video", UNSET))

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

        def _parse_video_mimetype(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        video_mimetype = _parse_video_mimetype(d.pop("video_mimetype", UNSET))

        def _parse_detail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        detail = _parse_detail(d.pop("detail", UNSET))

        def _parse_fps(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        fps = _parse_fps(d.pop("fps", UNSET))

        video_block = cls(
            block_type=block_type,
            video=video,
            path=path,
            url=url,
            video_mimetype=video_mimetype,
            detail=detail,
            fps=fps,
        )

        video_block.additional_properties = d
        return video_block

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
