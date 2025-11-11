from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mcp_tool_entity_association_response_tool_config_type_0 import (
        MCPToolEntityAssociationResponseToolConfigType0,
    )


T = TypeVar("T", bound="MCPToolEntityAssociationResponse")


@_attrs_define
class MCPToolEntityAssociationResponse:
    """
    Attributes:
        id (UUID):
        mcp_endpoint_name (str):
        tool_name (str):
        entity_definition_id (UUID):
        environment_id (UUID):
        created_at (str):
        updated_at (str):
        entity_version_id (None | Unset | UUID):
        tool_config (MCPToolEntityAssociationResponseToolConfigType0 | None | Unset):
    """

    id: UUID
    mcp_endpoint_name: str
    tool_name: str
    entity_definition_id: UUID
    environment_id: UUID
    created_at: str
    updated_at: str
    entity_version_id: None | Unset | UUID = UNSET
    tool_config: MCPToolEntityAssociationResponseToolConfigType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.mcp_tool_entity_association_response_tool_config_type_0 import (
            MCPToolEntityAssociationResponseToolConfigType0,
        )

        id = str(self.id)

        mcp_endpoint_name = self.mcp_endpoint_name

        tool_name = self.tool_name

        entity_definition_id = str(self.entity_definition_id)

        environment_id = str(self.environment_id)

        created_at = self.created_at

        updated_at = self.updated_at

        entity_version_id: None | str | Unset
        if isinstance(self.entity_version_id, Unset):
            entity_version_id = UNSET
        elif isinstance(self.entity_version_id, UUID):
            entity_version_id = str(self.entity_version_id)
        else:
            entity_version_id = self.entity_version_id

        tool_config: dict[str, Any] | None | Unset
        if isinstance(self.tool_config, Unset):
            tool_config = UNSET
        elif isinstance(self.tool_config, MCPToolEntityAssociationResponseToolConfigType0):
            tool_config = self.tool_config.to_dict()
        else:
            tool_config = self.tool_config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "mcp_endpoint_name": mcp_endpoint_name,
                "tool_name": tool_name,
                "entity_definition_id": entity_definition_id,
                "environment_id": environment_id,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if entity_version_id is not UNSET:
            field_dict["entity_version_id"] = entity_version_id
        if tool_config is not UNSET:
            field_dict["tool_config"] = tool_config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mcp_tool_entity_association_response_tool_config_type_0 import (
            MCPToolEntityAssociationResponseToolConfigType0,
        )

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        mcp_endpoint_name = d.pop("mcp_endpoint_name")

        tool_name = d.pop("tool_name")

        entity_definition_id = UUID(d.pop("entity_definition_id"))

        environment_id = UUID(d.pop("environment_id"))

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        def _parse_entity_version_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                entity_version_id_type_0 = UUID(data)

                return entity_version_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        entity_version_id = _parse_entity_version_id(d.pop("entity_version_id", UNSET))

        def _parse_tool_config(data: object) -> MCPToolEntityAssociationResponseToolConfigType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tool_config_type_0 = MCPToolEntityAssociationResponseToolConfigType0.from_dict(data)

                return tool_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MCPToolEntityAssociationResponseToolConfigType0 | None | Unset, data)

        tool_config = _parse_tool_config(d.pop("tool_config", UNSET))

        mcp_tool_entity_association_response = cls(
            id=id,
            mcp_endpoint_name=mcp_endpoint_name,
            tool_name=tool_name,
            entity_definition_id=entity_definition_id,
            environment_id=environment_id,
            created_at=created_at,
            updated_at=updated_at,
            entity_version_id=entity_version_id,
            tool_config=tool_config,
        )

        mcp_tool_entity_association_response.additional_properties = d
        return mcp_tool_entity_association_response

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
