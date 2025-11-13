from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cache_control import CacheControl


T = TypeVar("T", bound="CachePoint")


@_attrs_define
class CachePoint:
    """Used to set the point to cache up to, if the LLM supports caching.

    Attributes:
        cache_control (CacheControl):
        block_type (Literal['cache'] | Unset):  Default: 'cache'.
    """

    cache_control: CacheControl
    block_type: Literal["cache"] | Unset = "cache"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cache_control = self.cache_control.to_dict()

        block_type = self.block_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cache_control": cache_control,
            }
        )
        if block_type is not UNSET:
            field_dict["block_type"] = block_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cache_control import CacheControl

        d = dict(src_dict)
        cache_control = CacheControl.from_dict(d.pop("cache_control"))

        block_type = cast(Literal["cache"] | Unset, d.pop("block_type", UNSET))
        if block_type != "cache" and not isinstance(block_type, Unset):
            raise ValueError(f"block_type must match const 'cache', got '{block_type}'")

        cache_point = cls(
            cache_control=cache_control,
            block_type=block_type,
        )

        cache_point.additional_properties = d
        return cache_point

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
