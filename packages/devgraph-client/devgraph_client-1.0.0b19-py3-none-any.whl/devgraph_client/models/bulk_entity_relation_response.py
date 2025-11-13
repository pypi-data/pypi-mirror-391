from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bulk_entity_relation_response_failed_relations_item import (
        BulkEntityRelationResponseFailedRelationsItem,
    )
    from ..models.entity_relation_response import EntityRelationResponse


T = TypeVar("T", bound="BulkEntityRelationResponse")


@_attrs_define
class BulkEntityRelationResponse:
    """Response model for bulk entity relation creation.

    Attributes:
        total_requested (int): Total number of relations requested for creation.
        success_count (int): Number of successfully created relations.
        failure_count (int): Number of failed relation creations.
        namespace (str | Unset):  Default: 'default'.
        created_relations (list[EntityRelationResponse] | Unset): Successfully created relations
        failed_relations (list[BulkEntityRelationResponseFailedRelationsItem] | Unset): Relations that failed to create
            with error details
    """

    total_requested: int
    success_count: int
    failure_count: int
    namespace: str | Unset = "default"
    created_relations: list[EntityRelationResponse] | Unset = UNSET
    failed_relations: list[BulkEntityRelationResponseFailedRelationsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_requested = self.total_requested

        success_count = self.success_count

        failure_count = self.failure_count

        namespace = self.namespace

        created_relations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.created_relations, Unset):
            created_relations = []
            for created_relations_item_data in self.created_relations:
                created_relations_item = created_relations_item_data.to_dict()
                created_relations.append(created_relations_item)

        failed_relations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.failed_relations, Unset):
            failed_relations = []
            for failed_relations_item_data in self.failed_relations:
                failed_relations_item = failed_relations_item_data.to_dict()
                failed_relations.append(failed_relations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_requested": total_requested,
                "success_count": success_count,
                "failure_count": failure_count,
            }
        )
        if namespace is not UNSET:
            field_dict["namespace"] = namespace
        if created_relations is not UNSET:
            field_dict["created_relations"] = created_relations
        if failed_relations is not UNSET:
            field_dict["failed_relations"] = failed_relations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bulk_entity_relation_response_failed_relations_item import (
            BulkEntityRelationResponseFailedRelationsItem,
        )
        from ..models.entity_relation_response import EntityRelationResponse

        d = dict(src_dict)
        total_requested = d.pop("total_requested")

        success_count = d.pop("success_count")

        failure_count = d.pop("failure_count")

        namespace = d.pop("namespace", UNSET)

        _created_relations = d.pop("created_relations", UNSET)
        created_relations: list[EntityRelationResponse] | Unset = UNSET
        if _created_relations is not UNSET:
            created_relations = []
            for created_relations_item_data in _created_relations:
                created_relations_item = EntityRelationResponse.from_dict(created_relations_item_data)

                created_relations.append(created_relations_item)

        _failed_relations = d.pop("failed_relations", UNSET)
        failed_relations: list[BulkEntityRelationResponseFailedRelationsItem] | Unset = UNSET
        if _failed_relations is not UNSET:
            failed_relations = []
            for failed_relations_item_data in _failed_relations:
                failed_relations_item = BulkEntityRelationResponseFailedRelationsItem.from_dict(
                    failed_relations_item_data
                )

                failed_relations.append(failed_relations_item)

        bulk_entity_relation_response = cls(
            total_requested=total_requested,
            success_count=success_count,
            failure_count=failure_count,
            namespace=namespace,
            created_relations=created_relations,
            failed_relations=failed_relations,
        )

        bulk_entity_relation_response.additional_properties = d
        return bulk_entity_relation_response

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
