from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentResponse")


@_attrs_define
class EnvironmentResponse:
    """
    Attributes:
        id (UUID):
        name (str):
        slug (str):
        clerk_organization_id (str):
        customer_id (str):
        subscription_id (UUID):
        active (bool | Unset):  Default: True.
    """

    id: UUID
    name: str
    slug: str
    clerk_organization_id: str
    customer_id: str
    subscription_id: UUID
    active: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        slug = self.slug

        clerk_organization_id = self.clerk_organization_id

        customer_id = self.customer_id

        subscription_id = str(self.subscription_id)

        active = self.active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "slug": slug,
                "clerk_organization_id": clerk_organization_id,
                "customer_id": customer_id,
                "subscription_id": subscription_id,
            }
        )
        if active is not UNSET:
            field_dict["active"] = active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        slug = d.pop("slug")

        clerk_organization_id = d.pop("clerk_organization_id")

        customer_id = d.pop("customer_id")

        subscription_id = UUID(d.pop("subscription_id"))

        active = d.pop("active", UNSET)

        environment_response = cls(
            id=id,
            name=name,
            slug=slug,
            clerk_organization_id=clerk_organization_id,
            customer_id=customer_id,
            subscription_id=subscription_id,
            active=active,
        )

        environment_response.additional_properties = d
        return environment_response

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
