from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_metadata import EntityMetadata
    from ..models.entity_spec import EntitySpec
    from ..models.entity_status import EntityStatus


T = TypeVar("T", bound="Entity")


@_attrs_define
class Entity:
    """
    Attributes:
        api_version (str):
        kind (str):
        metadata (EntityMetadata):
        spec (EntitySpec | Unset):
        status (EntityStatus | Unset): Status information for an entity including lifecycle tracking.
    """

    api_version: str
    kind: str
    metadata: EntityMetadata
    spec: EntitySpec | Unset = UNSET
    status: EntityStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        api_version = self.api_version

        kind = self.kind

        metadata = self.metadata.to_dict()

        spec: dict[str, Any] | Unset = UNSET
        if not isinstance(self.spec, Unset):
            spec = self.spec.to_dict()

        status: dict[str, Any] | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "apiVersion": api_version,
                "kind": kind,
                "metadata": metadata,
            }
        )
        if spec is not UNSET:
            field_dict["spec"] = spec
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_metadata import EntityMetadata
        from ..models.entity_spec import EntitySpec
        from ..models.entity_status import EntityStatus

        d = dict(src_dict)
        api_version = d.pop("apiVersion")

        kind = d.pop("kind")

        metadata = EntityMetadata.from_dict(d.pop("metadata"))

        _spec = d.pop("spec", UNSET)
        spec: EntitySpec | Unset
        if isinstance(_spec, Unset):
            spec = UNSET
        else:
            spec = EntitySpec.from_dict(_spec)

        _status = d.pop("status", UNSET)
        status: EntityStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = EntityStatus.from_dict(_status)

        entity = cls(
            api_version=api_version,
            kind=kind,
            metadata=metadata,
            spec=spec,
            status=status,
        )

        entity.additional_properties = d
        return entity

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
