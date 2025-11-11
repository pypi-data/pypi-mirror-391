from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_metadata_annotations import EntityMetadataAnnotations
    from ..models.entity_metadata_labels import EntityMetadataLabels


T = TypeVar("T", bound="EntityMetadata")


@_attrs_define
class EntityMetadata:
    """
    Attributes:
        name (str):
        namespace (str):
        uid (str | Unset):
        labels (EntityMetadataLabels | Unset):
        annotations (EntityMetadataAnnotations | Unset):
    """

    name: str
    namespace: str
    uid: str | Unset = UNSET
    labels: EntityMetadataLabels | Unset = UNSET
    annotations: EntityMetadataAnnotations | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        namespace = self.namespace

        uid = self.uid

        labels: dict[str, Any] | Unset = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels.to_dict()

        annotations: dict[str, Any] | Unset = UNSET
        if not isinstance(self.annotations, Unset):
            annotations = self.annotations.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "namespace": namespace,
            }
        )
        if uid is not UNSET:
            field_dict["uid"] = uid
        if labels is not UNSET:
            field_dict["labels"] = labels
        if annotations is not UNSET:
            field_dict["annotations"] = annotations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_metadata_annotations import EntityMetadataAnnotations
        from ..models.entity_metadata_labels import EntityMetadataLabels

        d = dict(src_dict)
        name = d.pop("name")

        namespace = d.pop("namespace")

        uid = d.pop("uid", UNSET)

        _labels = d.pop("labels", UNSET)
        labels: EntityMetadataLabels | Unset
        if isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = EntityMetadataLabels.from_dict(_labels)

        _annotations = d.pop("annotations", UNSET)
        annotations: EntityMetadataAnnotations | Unset
        if isinstance(_annotations, Unset):
            annotations = UNSET
        else:
            annotations = EntityMetadataAnnotations.from_dict(_annotations)

        entity_metadata = cls(
            name=name,
            namespace=namespace,
            uid=uid,
            labels=labels,
            annotations=annotations,
        )

        entity_metadata.additional_properties = d
        return entity_metadata

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
