from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitlementCheckResponse")


@_attrs_define
class EntitlementCheckResponse:
    """
    Attributes:
        allowed (bool):
        limit (int | None | Unset):
        current_usage (int | None | Unset):
        remaining (int | None | Unset):
        reason (None | str | Unset):
    """

    allowed: bool
    limit: int | None | Unset = UNSET
    current_usage: int | None | Unset = UNSET
    remaining: int | None | Unset = UNSET
    reason: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allowed = self.allowed

        limit: int | None | Unset
        if isinstance(self.limit, Unset):
            limit = UNSET
        else:
            limit = self.limit

        current_usage: int | None | Unset
        if isinstance(self.current_usage, Unset):
            current_usage = UNSET
        else:
            current_usage = self.current_usage

        remaining: int | None | Unset
        if isinstance(self.remaining, Unset):
            remaining = UNSET
        else:
            remaining = self.remaining

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allowed": allowed,
            }
        )
        if limit is not UNSET:
            field_dict["limit"] = limit
        if current_usage is not UNSET:
            field_dict["current_usage"] = current_usage
        if remaining is not UNSET:
            field_dict["remaining"] = remaining
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allowed = d.pop("allowed")

        def _parse_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        limit = _parse_limit(d.pop("limit", UNSET))

        def _parse_current_usage(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        current_usage = _parse_current_usage(d.pop("current_usage", UNSET))

        def _parse_remaining(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        remaining = _parse_remaining(d.pop("remaining", UNSET))

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        entitlement_check_response = cls(
            allowed=allowed,
            limit=limit,
            current_usage=current_usage,
            remaining=remaining,
            reason=reason,
        )

        entitlement_check_response.additional_properties = d
        return entitlement_check_response

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
