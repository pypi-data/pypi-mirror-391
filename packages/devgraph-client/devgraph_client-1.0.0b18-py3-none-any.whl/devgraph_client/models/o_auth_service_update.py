from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.o_auth_service_update_additional_params_type_0 import OAuthServiceUpdateAdditionalParamsType0


T = TypeVar("T", bound="OAuthServiceUpdate")


@_attrs_define
class OAuthServiceUpdate:
    """
    Attributes:
        display_name (None | str | Unset):
        description (None | str | Unset):
        client_id (None | str | Unset):
        client_secret (None | str | Unset):
        authorization_url (None | str | Unset):
        token_url (None | str | Unset):
        userinfo_url (None | str | Unset):
        default_scopes (list[str] | None | Unset):
        supported_grant_types (list[str] | None | Unset):
        is_active (bool | None | Unset):
        icon_url (None | str | Unset):
        homepage_url (None | str | Unset):
        additional_params (None | OAuthServiceUpdateAdditionalParamsType0 | Unset):
    """

    display_name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    client_id: None | str | Unset = UNSET
    client_secret: None | str | Unset = UNSET
    authorization_url: None | str | Unset = UNSET
    token_url: None | str | Unset = UNSET
    userinfo_url: None | str | Unset = UNSET
    default_scopes: list[str] | None | Unset = UNSET
    supported_grant_types: list[str] | None | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    icon_url: None | str | Unset = UNSET
    homepage_url: None | str | Unset = UNSET
    additional_params: None | OAuthServiceUpdateAdditionalParamsType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.o_auth_service_update_additional_params_type_0 import OAuthServiceUpdateAdditionalParamsType0

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        client_id: None | str | Unset
        if isinstance(self.client_id, Unset):
            client_id = UNSET
        else:
            client_id = self.client_id

        client_secret: None | str | Unset
        if isinstance(self.client_secret, Unset):
            client_secret = UNSET
        else:
            client_secret = self.client_secret

        authorization_url: None | str | Unset
        if isinstance(self.authorization_url, Unset):
            authorization_url = UNSET
        else:
            authorization_url = self.authorization_url

        token_url: None | str | Unset
        if isinstance(self.token_url, Unset):
            token_url = UNSET
        else:
            token_url = self.token_url

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

        supported_grant_types: list[str] | None | Unset
        if isinstance(self.supported_grant_types, Unset):
            supported_grant_types = UNSET
        elif isinstance(self.supported_grant_types, list):
            supported_grant_types = self.supported_grant_types

        else:
            supported_grant_types = self.supported_grant_types

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
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
        elif isinstance(self.additional_params, OAuthServiceUpdateAdditionalParamsType0):
            additional_params = self.additional_params.to_dict()
        else:
            additional_params = self.additional_params

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if client_secret is not UNSET:
            field_dict["client_secret"] = client_secret
        if authorization_url is not UNSET:
            field_dict["authorization_url"] = authorization_url
        if token_url is not UNSET:
            field_dict["token_url"] = token_url
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
        from ..models.o_auth_service_update_additional_params_type_0 import OAuthServiceUpdateAdditionalParamsType0

        d = dict(src_dict)

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_client_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        client_id = _parse_client_id(d.pop("client_id", UNSET))

        def _parse_client_secret(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        client_secret = _parse_client_secret(d.pop("client_secret", UNSET))

        def _parse_authorization_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        authorization_url = _parse_authorization_url(d.pop("authorization_url", UNSET))

        def _parse_token_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        token_url = _parse_token_url(d.pop("token_url", UNSET))

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

        def _parse_supported_grant_types(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                supported_grant_types_type_0 = cast(list[str], data)

                return supported_grant_types_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        supported_grant_types = _parse_supported_grant_types(d.pop("supported_grant_types", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

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

        def _parse_additional_params(data: object) -> None | OAuthServiceUpdateAdditionalParamsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                additional_params_type_0 = OAuthServiceUpdateAdditionalParamsType0.from_dict(data)

                return additional_params_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OAuthServiceUpdateAdditionalParamsType0 | Unset, data)

        additional_params = _parse_additional_params(d.pop("additional_params", UNSET))

        o_auth_service_update = cls(
            display_name=display_name,
            description=description,
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=authorization_url,
            token_url=token_url,
            userinfo_url=userinfo_url,
            default_scopes=default_scopes,
            supported_grant_types=supported_grant_types,
            is_active=is_active,
            icon_url=icon_url,
            homepage_url=homepage_url,
            additional_params=additional_params,
        )

        o_auth_service_update.additional_properties = d
        return o_auth_service_update

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
