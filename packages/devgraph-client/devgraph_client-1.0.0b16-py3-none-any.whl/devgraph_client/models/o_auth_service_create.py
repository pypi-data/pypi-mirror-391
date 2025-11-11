from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.o_auth_service_create_additional_params_type_0 import OAuthServiceCreateAdditionalParamsType0


T = TypeVar("T", bound="OAuthServiceCreate")


@_attrs_define
class OAuthServiceCreate:
    """
    Attributes:
        name (str):
        display_name (str):
        client_id (str):
        client_secret (str):
        authorization_url (str):
        token_url (str):
        description (None | str | Unset):
        userinfo_url (None | str | Unset):
        default_scopes (list[str] | None | Unset):
        supported_grant_types (list[str] | Unset):
        is_active (bool | Unset):  Default: True.
        icon_url (None | str | Unset):
        homepage_url (None | str | Unset):
        additional_params (None | OAuthServiceCreateAdditionalParamsType0 | Unset):
    """

    name: str
    display_name: str
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    description: None | str | Unset = UNSET
    userinfo_url: None | str | Unset = UNSET
    default_scopes: list[str] | None | Unset = UNSET
    supported_grant_types: list[str] | Unset = UNSET
    is_active: bool | Unset = True
    icon_url: None | str | Unset = UNSET
    homepage_url: None | str | Unset = UNSET
    additional_params: None | OAuthServiceCreateAdditionalParamsType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.o_auth_service_create_additional_params_type_0 import OAuthServiceCreateAdditionalParamsType0

        name = self.name

        display_name = self.display_name

        client_id = self.client_id

        client_secret = self.client_secret

        authorization_url = self.authorization_url

        token_url = self.token_url

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        userinfo_url: None | str | Unset
        if isinstance(self.userinfo_url, Unset):
            userinfo_url = UNSET
        else:
            userinfo_url = self.userinfo_url

        default_scopes: list[str] | None | Unset
        if isinstance(self.default_scopes, Unset):
            default_scopes = UNSET
        elif isinstance(self.default_scopes, list):
            default_scopes = self.default_scopes

        else:
            default_scopes = self.default_scopes

        supported_grant_types: list[str] | Unset = UNSET
        if not isinstance(self.supported_grant_types, Unset):
            supported_grant_types = self.supported_grant_types

        is_active = self.is_active

        icon_url: None | str | Unset
        if isinstance(self.icon_url, Unset):
            icon_url = UNSET
        else:
            icon_url = self.icon_url

        homepage_url: None | str | Unset
        if isinstance(self.homepage_url, Unset):
            homepage_url = UNSET
        else:
            homepage_url = self.homepage_url

        additional_params: dict[str, Any] | None | Unset
        if isinstance(self.additional_params, Unset):
            additional_params = UNSET
        elif isinstance(self.additional_params, OAuthServiceCreateAdditionalParamsType0):
            additional_params = self.additional_params.to_dict()
        else:
            additional_params = self.additional_params

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "display_name": display_name,
                "client_id": client_id,
                "client_secret": client_secret,
                "authorization_url": authorization_url,
                "token_url": token_url,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if userinfo_url is not UNSET:
            field_dict["userinfo_url"] = userinfo_url
        if default_scopes is not UNSET:
            field_dict["default_scopes"] = default_scopes
        if supported_grant_types is not UNSET:
            field_dict["supported_grant_types"] = supported_grant_types
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if icon_url is not UNSET:
            field_dict["icon_url"] = icon_url
        if homepage_url is not UNSET:
            field_dict["homepage_url"] = homepage_url
        if additional_params is not UNSET:
            field_dict["additional_params"] = additional_params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.o_auth_service_create_additional_params_type_0 import OAuthServiceCreateAdditionalParamsType0

        d = dict(src_dict)
        name = d.pop("name")

        display_name = d.pop("display_name")

        client_id = d.pop("client_id")

        client_secret = d.pop("client_secret")

        authorization_url = d.pop("authorization_url")

        token_url = d.pop("token_url")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_userinfo_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        userinfo_url = _parse_userinfo_url(d.pop("userinfo_url", UNSET))

        def _parse_default_scopes(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                default_scopes_type_0 = cast(list[str], data)

                return default_scopes_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        default_scopes = _parse_default_scopes(d.pop("default_scopes", UNSET))

        supported_grant_types = cast(list[str], d.pop("supported_grant_types", UNSET))

        is_active = d.pop("is_active", UNSET)

        def _parse_icon_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_url = _parse_icon_url(d.pop("icon_url", UNSET))

        def _parse_homepage_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        homepage_url = _parse_homepage_url(d.pop("homepage_url", UNSET))

        def _parse_additional_params(data: object) -> None | OAuthServiceCreateAdditionalParamsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                additional_params_type_0 = OAuthServiceCreateAdditionalParamsType0.from_dict(data)

                return additional_params_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OAuthServiceCreateAdditionalParamsType0 | Unset, data)

        additional_params = _parse_additional_params(d.pop("additional_params", UNSET))

        o_auth_service_create = cls(
            name=name,
            display_name=display_name,
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=authorization_url,
            token_url=token_url,
            description=description,
            userinfo_url=userinfo_url,
            default_scopes=default_scopes,
            supported_grant_types=supported_grant_types,
            is_active=is_active,
            icon_url=icon_url,
            homepage_url=homepage_url,
            additional_params=additional_params,
        )

        o_auth_service_create.additional_properties = d
        return o_auth_service_create

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
