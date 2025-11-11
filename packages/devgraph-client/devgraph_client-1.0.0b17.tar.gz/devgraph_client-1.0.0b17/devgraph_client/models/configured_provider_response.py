from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.configured_provider_response_config import ConfiguredProviderResponseConfig


T = TypeVar("T", bound="ConfiguredProviderResponse")


@_attrs_define
class ConfiguredProviderResponse:
    """Response for a configured discovery provider (secrets masked).

    Attributes:
        id (UUID):
        environment_id (UUID):
        name (str):
        provider_type (str):
        enabled (bool):
        interval (int):
        config (ConfiguredProviderResponseConfig):
        last_run_at (None | str | Unset):
        last_run_status (None | str | Unset):
        last_error_message (None | str | Unset):
    """

    id: UUID
    environment_id: UUID
    name: str
    provider_type: str
    enabled: bool
    interval: int
    config: ConfiguredProviderResponseConfig
    last_run_at: None | str | Unset = UNSET
    last_run_status: None | str | Unset = UNSET
    last_error_message: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        environment_id = str(self.environment_id)

        name = self.name

        provider_type = self.provider_type

        enabled = self.enabled

        interval = self.interval

        config = self.config.to_dict()

        last_run_at: None | str | Unset
        if isinstance(self.last_run_at, Unset):
            last_run_at = UNSET
        else:
            last_run_at = self.last_run_at

        last_run_status: None | str | Unset
        if isinstance(self.last_run_status, Unset):
            last_run_status = UNSET
        else:
            last_run_status = self.last_run_status

        last_error_message: None | str | Unset
        if isinstance(self.last_error_message, Unset):
            last_error_message = UNSET
        else:
            last_error_message = self.last_error_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "environment_id": environment_id,
                "name": name,
                "provider_type": provider_type,
                "enabled": enabled,
                "interval": interval,
                "config": config,
            }
        )
        if last_run_at is not UNSET:
            field_dict["last_run_at"] = last_run_at
        if last_run_status is not UNSET:
            field_dict["last_run_status"] = last_run_status
        if last_error_message is not UNSET:
            field_dict["last_error_message"] = last_error_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.configured_provider_response_config import ConfiguredProviderResponseConfig

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        environment_id = UUID(d.pop("environment_id"))

        name = d.pop("name")

        provider_type = d.pop("provider_type")

        enabled = d.pop("enabled")

        interval = d.pop("interval")

        config = ConfiguredProviderResponseConfig.from_dict(d.pop("config"))

        def _parse_last_run_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_run_at = _parse_last_run_at(d.pop("last_run_at", UNSET))

        def _parse_last_run_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_run_status = _parse_last_run_status(d.pop("last_run_status", UNSET))

        def _parse_last_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_error_message = _parse_last_error_message(d.pop("last_error_message", UNSET))

        configured_provider_response = cls(
            id=id,
            environment_id=environment_id,
            name=name,
            provider_type=provider_type,
            enabled=enabled,
            interval=interval,
            config=config,
            last_run_at=last_run_at,
            last_run_status=last_run_status,
            last_error_message=last_error_message,
        )

        configured_provider_response.additional_properties = d
        return configured_provider_response

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
