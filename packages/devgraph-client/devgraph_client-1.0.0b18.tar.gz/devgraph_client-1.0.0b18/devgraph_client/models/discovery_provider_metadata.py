from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.discovery_provider_metadata_config_schema import DiscoveryProviderMetadataConfigSchema


T = TypeVar("T", bound="DiscoveryProviderMetadata")


@_attrs_define
class DiscoveryProviderMetadata:
    """Metadata about a discovery provider.

    Attributes:
        type_ (str):
        display_name (str):
        description (str):
        config_schema (DiscoveryProviderMetadataConfigSchema):
        logo (None | str | Unset):
    """

    type_: str
    display_name: str
    description: str
    config_schema: DiscoveryProviderMetadataConfigSchema
    logo: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        display_name = self.display_name

        description = self.description

        config_schema = self.config_schema.to_dict()

        logo: None | str | Unset
        if isinstance(self.logo, Unset):
            logo = UNSET
        else:
            logo = self.logo

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "display_name": display_name,
                "description": description,
                "config_schema": config_schema,
            }
        )
        if logo is not UNSET:
            field_dict["logo"] = logo

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.discovery_provider_metadata_config_schema import DiscoveryProviderMetadataConfigSchema

        d = dict(src_dict)
        type_ = d.pop("type")

        display_name = d.pop("display_name")

        description = d.pop("description")

        config_schema = DiscoveryProviderMetadataConfigSchema.from_dict(d.pop("config_schema"))

        def _parse_logo(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        logo = _parse_logo(d.pop("logo", UNSET))

        discovery_provider_metadata = cls(
            type_=type_,
            display_name=display_name,
            description=description,
            config_schema=config_schema,
            logo=logo,
        )

        discovery_provider_metadata.additional_properties = d
        return discovery_provider_metadata

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
