from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EnvironmentUserResponse")


@_attrs_define
class EnvironmentUserResponse:
    """
    Attributes:
        id (str):
        email_address (str):
        role (str):
        status (str):
        created_at (int):
        updated_at (int):
    """

    id: str
    email_address: str
    role: str
    status: str
    created_at: int
    updated_at: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email_address = self.email_address

        role = self.role

        status = self.status

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "email_address": email_address,
                "role": role,
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        email_address = d.pop("email_address")

        role = d.pop("role")

        status = d.pop("status")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        environment_user_response = cls(
            id=id,
            email_address=email_address,
            role=role,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
        )

        environment_user_response.additional_properties = d
        return environment_user_response

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
