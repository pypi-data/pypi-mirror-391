from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EntityStatus")


@_attrs_define
class EntityStatus:
    """Status information for an entity including lifecycle tracking.

    Attributes:
        last_updated (datetime.datetime | Unset): Timestamp when the entity was last updated
        is_orphan (bool | Unset): Whether this entity is orphaned (definition no longer exists) Default: False.
        last_seen (datetime.datetime | None | Unset):
        discovery_source (None | str | Unset):
        generation (int | Unset): Generation number, incremented on each update Default: 1.
    """

    last_updated: datetime.datetime | Unset = UNSET
    is_orphan: bool | Unset = False
    last_seen: datetime.datetime | None | Unset = UNSET
    discovery_source: None | str | Unset = UNSET
    generation: int | Unset = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        last_updated: str | Unset = UNSET
        if not isinstance(self.last_updated, Unset):
            last_updated = self.last_updated.isoformat()

        is_orphan = self.is_orphan

        last_seen: None | str | Unset
        if isinstance(self.last_seen, Unset):
            last_seen = UNSET
        elif isinstance(self.last_seen, datetime.datetime):
            last_seen = self.last_seen.isoformat()
        else:
            last_seen = self.last_seen

        discovery_source: None | str | Unset
        if isinstance(self.discovery_source, Unset):
            discovery_source = UNSET
        else:
            discovery_source = self.discovery_source

        generation = self.generation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if last_updated is not UNSET:
            field_dict["last_updated"] = last_updated
        if is_orphan is not UNSET:
            field_dict["is_orphan"] = is_orphan
        if last_seen is not UNSET:
            field_dict["last_seen"] = last_seen
        if discovery_source is not UNSET:
            field_dict["discovery_source"] = discovery_source
        if generation is not UNSET:
            field_dict["generation"] = generation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _last_updated = d.pop("last_updated", UNSET)
        last_updated: datetime.datetime | Unset
        if isinstance(_last_updated, Unset):
            last_updated = UNSET
        else:
            last_updated = isoparse(_last_updated)

        is_orphan = d.pop("is_orphan", UNSET)

        def _parse_last_seen(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_seen_type_0 = isoparse(data)

                return last_seen_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_seen = _parse_last_seen(d.pop("last_seen", UNSET))

        def _parse_discovery_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        discovery_source = _parse_discovery_source(d.pop("discovery_source", UNSET))

        generation = d.pop("generation", UNSET)

        entity_status = cls(
            last_updated=last_updated,
            is_orphan=is_orphan,
            last_seen=last_seen,
            discovery_source=discovery_source,
            generation=generation,
        )

        entity_status.additional_properties = d
        return entity_status

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
