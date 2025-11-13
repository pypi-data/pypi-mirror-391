from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="OAuthServiceResponse")


@_attrs_define
class OAuthServiceResponse:
    """
    Attributes:
        id (UUID):
        name (str):
        display_name (str):
        description (None | str):
        authorization_url (str):
        token_url (str):
        userinfo_url (None | str):
        default_scopes (list[str]):
        supported_grant_types (list[str]):
        is_active (bool):
        icon_url (None | str):
        homepage_url (None | str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: UUID
    name: str
    display_name: str
    description: None | str
    authorization_url: str
    token_url: str
    userinfo_url: None | str
    default_scopes: list[str]
    supported_grant_types: list[str]
    is_active: bool
    icon_url: None | str
    homepage_url: None | str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        display_name = self.display_name

        description: None | str
        description = self.description

        authorization_url = self.authorization_url

        token_url = self.token_url

        userinfo_url: None | str
        userinfo_url = self.userinfo_url

        default_scopes = self.default_scopes

        supported_grant_types = self.supported_grant_types

        is_active = self.is_active

        icon_url: None | str
        icon_url = self.icon_url

        homepage_url: None | str
        homepage_url = self.homepage_url

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "display_name": display_name,
                "description": description,
                "authorization_url": authorization_url,
                "token_url": token_url,
                "userinfo_url": userinfo_url,
                "default_scopes": default_scopes,
                "supported_grant_types": supported_grant_types,
                "is_active": is_active,
                "icon_url": icon_url,
                "homepage_url": homepage_url,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        display_name = d.pop("display_name")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        authorization_url = d.pop("authorization_url")

        token_url = d.pop("token_url")

        def _parse_userinfo_url(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        userinfo_url = _parse_userinfo_url(d.pop("userinfo_url"))

        default_scopes = cast(list[str], d.pop("default_scopes"))

        supported_grant_types = cast(list[str], d.pop("supported_grant_types"))

        is_active = d.pop("is_active")

        def _parse_icon_url(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        icon_url = _parse_icon_url(d.pop("icon_url"))

        def _parse_homepage_url(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        homepage_url = _parse_homepage_url(d.pop("homepage_url"))

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        o_auth_service_response = cls(
            id=id,
            name=name,
            display_name=display_name,
            description=description,
            authorization_url=authorization_url,
            token_url=token_url,
            userinfo_url=userinfo_url,
            default_scopes=default_scopes,
            supported_grant_types=supported_grant_types,
            is_active=is_active,
            icon_url=icon_url,
            homepage_url=homepage_url,
            created_at=created_at,
            updated_at=updated_at,
        )

        o_auth_service_response.additional_properties = d
        return o_auth_service_response

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
