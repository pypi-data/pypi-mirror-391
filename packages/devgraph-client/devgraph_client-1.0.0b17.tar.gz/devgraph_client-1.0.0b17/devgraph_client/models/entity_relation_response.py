from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_reference_response import EntityReferenceResponse


T = TypeVar("T", bound="EntityRelationResponse")


@_attrs_define
class EntityRelationResponse:
    """
    Attributes:
        relation (str):
        source (EntityReferenceResponse):
        target (EntityReferenceResponse):
        namespace (str | Unset):  Default: 'default'.
    """

    relation: str
    source: EntityReferenceResponse
    target: EntityReferenceResponse
    namespace: str | Unset = "default"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        relation = self.relation

        source = self.source.to_dict()

        target = self.target.to_dict()

        namespace = self.namespace

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "relation": relation,
                "source": source,
                "target": target,
            }
        )
        if namespace is not UNSET:
            field_dict["namespace"] = namespace

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_reference_response import EntityReferenceResponse

        d = dict(src_dict)
        relation = d.pop("relation")

        source = EntityReferenceResponse.from_dict(d.pop("source"))

        target = EntityReferenceResponse.from_dict(d.pop("target"))

        namespace = d.pop("namespace", UNSET)

        entity_relation_response = cls(
            relation=relation,
            source=source,
            target=target,
            namespace=namespace,
        )

        entity_relation_response.additional_properties = d
        return entity_relation_response

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
