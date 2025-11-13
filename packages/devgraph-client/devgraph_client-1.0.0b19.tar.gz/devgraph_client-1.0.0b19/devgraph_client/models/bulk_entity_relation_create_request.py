from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_relation import EntityRelation


T = TypeVar("T", bound="BulkEntityRelationCreateRequest")


@_attrs_define
class BulkEntityRelationCreateRequest:
    """Request model for creating multiple entity relations in bulk.

    Attributes:
        relations (list[EntityRelation]): List of entity relations to create
        namespace (str | Unset):  Default: 'default'.
    """

    relations: list[EntityRelation]
    namespace: str | Unset = "default"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        relations = []
        for relations_item_data in self.relations:
            relations_item = relations_item_data.to_dict()
            relations.append(relations_item)

        namespace = self.namespace

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "relations": relations,
            }
        )
        if namespace is not UNSET:
            field_dict["namespace"] = namespace

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_relation import EntityRelation

        d = dict(src_dict)
        relations = []
        _relations = d.pop("relations")
        for relations_item_data in _relations:
            relations_item = EntityRelation.from_dict(relations_item_data)

            relations.append(relations_item)

        namespace = d.pop("namespace", UNSET)

        bulk_entity_relation_create_request = cls(
            relations=relations,
            namespace=namespace,
        )

        bulk_entity_relation_create_request.additional_properties = d
        return bulk_entity_relation_create_request

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
