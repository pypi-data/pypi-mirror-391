from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_definition_spec_spec import EntityDefinitionSpecSpec


T = TypeVar("T", bound="EntityDefinitionSpec")


@_attrs_define
class EntityDefinitionSpec:
    """
    Attributes:
        group (str):
        kind (str):
        list_kind (str):
        singular (str):
        spec (EntityDefinitionSpecSpec):
        plural (None | str | Unset):
        name (str | Unset):  Default: 'v1'.
        description (None | str | Unset):
        storage (bool | Unset):  Default: True.
        served (bool | Unset):  Default: True.
    """

    group: str
    kind: str
    list_kind: str
    singular: str
    spec: EntityDefinitionSpecSpec
    plural: None | str | Unset = UNSET
    name: str | Unset = "v1"
    description: None | str | Unset = UNSET
    storage: bool | Unset = True
    served: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group = self.group

        kind = self.kind

        list_kind = self.list_kind

        singular = self.singular

        spec = self.spec.to_dict()

        plural: None | str | Unset
        if isinstance(self.plural, Unset):
            plural = UNSET
        else:
            plural = self.plural

        name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        storage = self.storage

        served = self.served

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "group": group,
                "kind": kind,
                "list_kind": list_kind,
                "singular": singular,
                "spec": spec,
            }
        )
        if plural is not UNSET:
            field_dict["plural"] = plural
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if storage is not UNSET:
            field_dict["storage"] = storage
        if served is not UNSET:
            field_dict["served"] = served

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_definition_spec_spec import EntityDefinitionSpecSpec

        d = dict(src_dict)
        group = d.pop("group")

        kind = d.pop("kind")

        list_kind = d.pop("list_kind")

        singular = d.pop("singular")

        spec = EntityDefinitionSpecSpec.from_dict(d.pop("spec"))

        def _parse_plural(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        plural = _parse_plural(d.pop("plural", UNSET))

        name = d.pop("name", UNSET)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        storage = d.pop("storage", UNSET)

        served = d.pop("served", UNSET)

        entity_definition_spec = cls(
            group=group,
            kind=kind,
            list_kind=list_kind,
            singular=singular,
            spec=spec,
            plural=plural,
            name=name,
            description=description,
            storage=storage,
            served=served,
        )

        entity_definition_spec.additional_properties = d
        return entity_definition_spec

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
