from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mcp_endpoint_create_headers import MCPEndpointCreateHeaders


T = TypeVar("T", bound="MCPEndpointCreate")


@_attrs_define
class MCPEndpointCreate:
    """
    Attributes:
        name (str):
        url (str):
        description (None | str | Unset):
        headers (MCPEndpointCreateHeaders | Unset):
        devgraph_auth (bool | Unset):  Default: False.
        supports_resources (bool | Unset):  Default: False.
        oauth_service_id (None | Unset | UUID):
        immutable (bool | Unset):  Default: False.
        active (bool | Unset):  Default: True.
        allowed_tools (list[str] | None | Unset):
        denied_tools (list[str] | None | Unset):
    """

    name: str
    url: str
    description: None | str | Unset = UNSET
    headers: MCPEndpointCreateHeaders | Unset = UNSET
    devgraph_auth: bool | Unset = False
    supports_resources: bool | Unset = False
    oauth_service_id: None | Unset | UUID = UNSET
    immutable: bool | Unset = False
    active: bool | Unset = True
    allowed_tools: list[str] | None | Unset = UNSET
    denied_tools: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        url = self.url

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        headers: dict[str, Any] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = self.headers.to_dict()

        devgraph_auth = self.devgraph_auth

        supports_resources = self.supports_resources

        oauth_service_id: None | str | Unset
        if isinstance(self.oauth_service_id, Unset):
            oauth_service_id = UNSET
        elif isinstance(self.oauth_service_id, UUID):
            oauth_service_id = str(self.oauth_service_id)
        else:
            oauth_service_id = self.oauth_service_id

        immutable = self.immutable

        active = self.active

        allowed_tools: list[str] | None | Unset
        if isinstance(self.allowed_tools, Unset):
            allowed_tools = UNSET
        elif isinstance(self.allowed_tools, list):
            allowed_tools = self.allowed_tools

        else:
            allowed_tools = self.allowed_tools

        denied_tools: list[str] | None | Unset
        if isinstance(self.denied_tools, Unset):
            denied_tools = UNSET
        elif isinstance(self.denied_tools, list):
            denied_tools = self.denied_tools

        else:
            denied_tools = self.denied_tools

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "url": url,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if headers is not UNSET:
            field_dict["headers"] = headers
        if devgraph_auth is not UNSET:
            field_dict["devgraph_auth"] = devgraph_auth
        if supports_resources is not UNSET:
            field_dict["supports_resources"] = supports_resources
        if oauth_service_id is not UNSET:
            field_dict["oauth_service_id"] = oauth_service_id
        if immutable is not UNSET:
            field_dict["immutable"] = immutable
        if active is not UNSET:
            field_dict["active"] = active
        if allowed_tools is not UNSET:
            field_dict["allowed_tools"] = allowed_tools
        if denied_tools is not UNSET:
            field_dict["denied_tools"] = denied_tools

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mcp_endpoint_create_headers import MCPEndpointCreateHeaders

        d = dict(src_dict)
        name = d.pop("name")

        url = d.pop("url")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        _headers = d.pop("headers", UNSET)
        headers: MCPEndpointCreateHeaders | Unset
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = MCPEndpointCreateHeaders.from_dict(_headers)

        devgraph_auth = d.pop("devgraph_auth", UNSET)

        supports_resources = d.pop("supports_resources", UNSET)

        def _parse_oauth_service_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                oauth_service_id_type_0 = UUID(data)

                return oauth_service_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        oauth_service_id = _parse_oauth_service_id(d.pop("oauth_service_id", UNSET))

        immutable = d.pop("immutable", UNSET)

        active = d.pop("active", UNSET)

        def _parse_allowed_tools(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                allowed_tools_type_0 = cast(list[str], data)

                return allowed_tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        allowed_tools = _parse_allowed_tools(d.pop("allowed_tools", UNSET))

        def _parse_denied_tools(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                denied_tools_type_0 = cast(list[str], data)

                return denied_tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        denied_tools = _parse_denied_tools(d.pop("denied_tools", UNSET))

        mcp_endpoint_create = cls(
            name=name,
            url=url,
            description=description,
            headers=headers,
            devgraph_auth=devgraph_auth,
            supports_resources=supports_resources,
            oauth_service_id=oauth_service_id,
            immutable=immutable,
            active=active,
            allowed_tools=allowed_tools,
            denied_tools=denied_tools,
        )

        mcp_endpoint_create.additional_properties = d
        return mcp_endpoint_create

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
