from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.response_format_type import ResponseFormatType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ResponseFormat")


@_attrs_define
class ResponseFormat:
    """
    Attributes:
        type_ (ResponseFormatType | Unset): The format of the response Default: ResponseFormatType.TEXT.
    """

    type_: ResponseFormatType | Unset = ResponseFormatType.TEXT
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _type_ = d.pop("type", UNSET)
        type_: ResponseFormatType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = ResponseFormatType(_type_)

        response_format = cls(
            type_=type_,
        )

        response_format.additional_properties = d
        return response_format

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
