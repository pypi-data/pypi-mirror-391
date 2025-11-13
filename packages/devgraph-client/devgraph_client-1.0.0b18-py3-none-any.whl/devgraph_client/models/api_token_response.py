from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiTokenResponse")


@_attrs_define
class ApiTokenResponse:
    """
    Attributes:
        id (UUID):
        name (str):
        user_id (str):
        token (str):
        expires_at (None | str | Unset):
        scopes (list[str] | None | Unset):
        active (bool | Unset):  Default: True.
    """

    id: UUID
    name: str
    user_id: str
    token: str
    expires_at: None | str | Unset = UNSET
    scopes: list[str] | None | Unset = UNSET
    active: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        user_id = self.user_id

        token = self.token

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        else:
            expires_at = self.expires_at

        scopes: list[str] | None | Unset
        if isinstance(self.scopes, Unset):
            scopes = UNSET
        elif isinstance(self.scopes, list):
            scopes = self.scopes

        else:
            scopes = self.scopes

        active = self.active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "user_id": user_id,
                "token": token,
            }
        )
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if active is not UNSET:
            field_dict["active"] = active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        user_id = d.pop("user_id")

        token = d.pop("token")

        def _parse_expires_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        def _parse_scopes(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                scopes_type_0 = cast(list[str], data)

                return scopes_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        scopes = _parse_scopes(d.pop("scopes", UNSET))

        active = d.pop("active", UNSET)

        api_token_response = cls(
            id=id,
            name=name,
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            scopes=scopes,
            active=active,
        )

        api_token_response.additional_properties = d
        return api_token_response

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
