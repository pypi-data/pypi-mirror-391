from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentCreate")


@_attrs_define
class EnvironmentCreate:
    """
    Attributes:
        name (str):
        stripe_subscription_id (str):
        instance_url (str):
        invited_users (list[str] | Unset):
    """

    name: str
    stripe_subscription_id: str
    instance_url: str
    invited_users: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        stripe_subscription_id = self.stripe_subscription_id

        instance_url = self.instance_url

        invited_users: list[str] | Unset = UNSET
        if not isinstance(self.invited_users, Unset):
            invited_users = self.invited_users

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "stripe_subscription_id": stripe_subscription_id,
                "instance_url": instance_url,
            }
        )
        if invited_users is not UNSET:
            field_dict["invited_users"] = invited_users

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        stripe_subscription_id = d.pop("stripe_subscription_id")

        instance_url = d.pop("instance_url")

        invited_users = cast(list[str], d.pop("invited_users", UNSET))

        environment_create = cls(
            name=name,
            stripe_subscription_id=stripe_subscription_id,
            instance_url=instance_url,
            invited_users=invited_users,
        )

        environment_create.additional_properties = d
        return environment_create

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
