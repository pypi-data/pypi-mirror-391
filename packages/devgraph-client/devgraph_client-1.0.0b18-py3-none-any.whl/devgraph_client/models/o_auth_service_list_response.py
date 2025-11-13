from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.o_auth_service_response import OAuthServiceResponse


T = TypeVar("T", bound="OAuthServiceListResponse")


@_attrs_define
class OAuthServiceListResponse:
    """
    Attributes:
        services (list[OAuthServiceResponse]):
        total (int):
    """

    services: list[OAuthServiceResponse]
    total: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        services = []
        for services_item_data in self.services:
            services_item = services_item_data.to_dict()
            services.append(services_item)

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "services": services,
                "total": total,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.o_auth_service_response import OAuthServiceResponse

        d = dict(src_dict)
        services = []
        _services = d.pop("services")
        for services_item_data in _services:
            services_item = OAuthServiceResponse.from_dict(services_item_data)

            services.append(services_item)

        total = d.pop("total")

        o_auth_service_list_response = cls(
            services=services,
            total=total,
        )

        o_auth_service_list_response.additional_properties = d
        return o_auth_service_list_response

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
