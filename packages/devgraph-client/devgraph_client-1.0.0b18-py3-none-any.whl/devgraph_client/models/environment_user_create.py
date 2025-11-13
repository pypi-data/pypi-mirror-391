from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.environment_user_create_role import EnvironmentUserCreateRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentUserCreate")


@_attrs_define
class EnvironmentUserCreate:
    """
    Attributes:
        email_address (str):
        role (EnvironmentUserCreateRole | Unset):  Default: EnvironmentUserCreateRole.MEMBER.
    """

    email_address: str
    role: EnvironmentUserCreateRole | Unset = EnvironmentUserCreateRole.MEMBER
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email_address = self.email_address

        role: str | Unset = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email_address": email_address,
            }
        )
        if role is not UNSET:
            field_dict["role"] = role

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email_address = d.pop("email_address")

        _role = d.pop("role", UNSET)
        role: EnvironmentUserCreateRole | Unset
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = EnvironmentUserCreateRole(_role)

        environment_user_create = cls(
            email_address=email_address,
            role=role,
        )

        environment_user_create.additional_properties = d
        return environment_user_create

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
