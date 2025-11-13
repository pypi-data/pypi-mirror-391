from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tool_call_block_tool_kwargs_type_0 import ToolCallBlockToolKwargsType0


T = TypeVar("T", bound="ToolCallBlock")


@_attrs_define
class ToolCallBlock:
    """
    Attributes:
        tool_name (str): Name of the called tool
        block_type (Literal['tool_call'] | Unset):  Default: 'tool_call'.
        tool_call_id (None | str | Unset):
        tool_kwargs (str | ToolCallBlockToolKwargsType0 | Unset): Arguments provided to the tool, if available
    """

    tool_name: str
    block_type: Literal["tool_call"] | Unset = "tool_call"
    tool_call_id: None | str | Unset = UNSET
    tool_kwargs: str | ToolCallBlockToolKwargsType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.tool_call_block_tool_kwargs_type_0 import ToolCallBlockToolKwargsType0

        tool_name = self.tool_name

        block_type = self.block_type

        tool_call_id: None | str | Unset
        if isinstance(self.tool_call_id, Unset):
            tool_call_id = UNSET
        else:
            tool_call_id = self.tool_call_id

        tool_kwargs: dict[str, Any] | str | Unset
        if isinstance(self.tool_kwargs, Unset):
            tool_kwargs = UNSET
        elif isinstance(self.tool_kwargs, ToolCallBlockToolKwargsType0):
            tool_kwargs = self.tool_kwargs.to_dict()
        else:
            tool_kwargs = self.tool_kwargs

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tool_name": tool_name,
            }
        )
        if block_type is not UNSET:
            field_dict["block_type"] = block_type
        if tool_call_id is not UNSET:
            field_dict["tool_call_id"] = tool_call_id
        if tool_kwargs is not UNSET:
            field_dict["tool_kwargs"] = tool_kwargs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_call_block_tool_kwargs_type_0 import ToolCallBlockToolKwargsType0

        d = dict(src_dict)
        tool_name = d.pop("tool_name")

        block_type = cast(Literal["tool_call"] | Unset, d.pop("block_type", UNSET))
        if block_type != "tool_call" and not isinstance(block_type, Unset):
            raise ValueError(f"block_type must match const 'tool_call', got '{block_type}'")

        def _parse_tool_call_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        tool_call_id = _parse_tool_call_id(d.pop("tool_call_id", UNSET))

        def _parse_tool_kwargs(data: object) -> str | ToolCallBlockToolKwargsType0 | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tool_kwargs_type_0 = ToolCallBlockToolKwargsType0.from_dict(data)

                return tool_kwargs_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(str | ToolCallBlockToolKwargsType0 | Unset, data)

        tool_kwargs = _parse_tool_kwargs(d.pop("tool_kwargs", UNSET))

        tool_call_block = cls(
            tool_name=tool_name,
            block_type=block_type,
            tool_call_id=tool_call_id,
            tool_kwargs=tool_kwargs,
        )

        tool_call_block.additional_properties = d
        return tool_call_block

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
