from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_relation_response import EntityRelationResponse
    from ..models.entity_response import EntityResponse


T = TypeVar("T", bound="EntityResultSetResponse")


@_attrs_define
class EntityResultSetResponse:
    """Response for a set of entities with their relations (used for queries returning multiple entities).

    Attributes:
        primary_entities (list[EntityResponse] | Unset):
        related_entities (list[EntityResponse] | Unset):
        relations (list[EntityRelationResponse] | Unset):
    """

    primary_entities: list[EntityResponse] | Unset = UNSET
    related_entities: list[EntityResponse] | Unset = UNSET
    relations: list[EntityRelationResponse] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        primary_entities: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.primary_entities, Unset):
            primary_entities = []
            for primary_entities_item_data in self.primary_entities:
                primary_entities_item = primary_entities_item_data.to_dict()
                primary_entities.append(primary_entities_item)

        related_entities: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.related_entities, Unset):
            related_entities = []
            for related_entities_item_data in self.related_entities:
                related_entities_item = related_entities_item_data.to_dict()
                related_entities.append(related_entities_item)

        relations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.relations, Unset):
            relations = []
            for relations_item_data in self.relations:
                relations_item = relations_item_data.to_dict()
                relations.append(relations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if primary_entities is not UNSET:
            field_dict["primary_entities"] = primary_entities
        if related_entities is not UNSET:
            field_dict["related_entities"] = related_entities
        if relations is not UNSET:
            field_dict["relations"] = relations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_relation_response import EntityRelationResponse
        from ..models.entity_response import EntityResponse

        d = dict(src_dict)
        _primary_entities = d.pop("primary_entities", UNSET)
        primary_entities: list[EntityResponse] | Unset = UNSET
        if _primary_entities is not UNSET:
            primary_entities = []
            for primary_entities_item_data in _primary_entities:
                primary_entities_item = EntityResponse.from_dict(primary_entities_item_data)

                primary_entities.append(primary_entities_item)

        _related_entities = d.pop("related_entities", UNSET)
        related_entities: list[EntityResponse] | Unset = UNSET
        if _related_entities is not UNSET:
            related_entities = []
            for related_entities_item_data in _related_entities:
                related_entities_item = EntityResponse.from_dict(related_entities_item_data)

                related_entities.append(related_entities_item)

        _relations = d.pop("relations", UNSET)
        relations: list[EntityRelationResponse] | Unset = UNSET
        if _relations is not UNSET:
            relations = []
            for relations_item_data in _relations:
                relations_item = EntityRelationResponse.from_dict(relations_item_data)

                relations.append(relations_item)

        entity_result_set_response = cls(
            primary_entities=primary_entities,
            related_entities=related_entities,
            relations=relations,
        )

        entity_result_set_response.additional_properties = d
        return entity_result_set_response

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
