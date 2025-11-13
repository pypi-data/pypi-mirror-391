from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="XAIModelProviderResponse")


@_attrs_define
class XAIModelProviderResponse:
    """
    Attributes:
        type_ (Literal['xai']):
        id (UUID):
        name (str):
        api_key (str):
        default (bool | Unset):  Default: False.
    """

    type_: Literal["xai"]
    id: UUID
    name: str
    api_key: str
    default: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        id = str(self.id)

        name = self.name

        api_key = self.api_key

        default = self.default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "id": id,
                "name": name,
                "api_key": api_key,
            }
        )
        if default is not UNSET:
            field_dict["default"] = default

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["xai"], d.pop("type"))
        if type_ != "xai":
            raise ValueError(f"type must match const 'xai', got '{type_}'")

        id = UUID(d.pop("id"))

        name = d.pop("name")

        api_key = d.pop("api_key")

        default = d.pop("default", UNSET)

        xai_model_provider_response = cls(
            type_=type_,
            id=id,
            name=name,
            api_key=api_key,
            default=default,
        )

        xai_model_provider_response.additional_properties = d
        return xai_model_provider_response

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
