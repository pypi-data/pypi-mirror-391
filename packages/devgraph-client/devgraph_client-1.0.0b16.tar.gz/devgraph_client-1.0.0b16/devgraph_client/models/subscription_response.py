from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entitlement_response import EntitlementResponse


T = TypeVar("T", bound="SubscriptionResponse")


@_attrs_define
class SubscriptionResponse:
    """
    Attributes:
        id (UUID):
        stripe_subscription_id (str):
        status (str):
        environment_ids (list[UUID] | Unset):
        plan_name (None | str | Unset):
        current_period_start (int | None | Unset):
        current_period_end (int | None | Unset):
        entitlements (list[EntitlementResponse] | Unset):
    """

    id: UUID
    stripe_subscription_id: str
    status: str
    environment_ids: list[UUID] | Unset = UNSET
    plan_name: None | str | Unset = UNSET
    current_period_start: int | None | Unset = UNSET
    current_period_end: int | None | Unset = UNSET
    entitlements: list[EntitlementResponse] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        stripe_subscription_id = self.stripe_subscription_id

        status = self.status

        environment_ids: list[str] | Unset = UNSET
        if not isinstance(self.environment_ids, Unset):
            environment_ids = []
            for environment_ids_item_data in self.environment_ids:
                environment_ids_item = str(environment_ids_item_data)
                environment_ids.append(environment_ids_item)

        plan_name: None | str | Unset
        if isinstance(self.plan_name, Unset):
            plan_name = UNSET
        else:
            plan_name = self.plan_name

        current_period_start: int | None | Unset
        if isinstance(self.current_period_start, Unset):
            current_period_start = UNSET
        else:
            current_period_start = self.current_period_start

        current_period_end: int | None | Unset
        if isinstance(self.current_period_end, Unset):
            current_period_end = UNSET
        else:
            current_period_end = self.current_period_end

        entitlements: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.entitlements, Unset):
            entitlements = []
            for entitlements_item_data in self.entitlements:
                entitlements_item = entitlements_item_data.to_dict()
                entitlements.append(entitlements_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "stripe_subscription_id": stripe_subscription_id,
                "status": status,
            }
        )
        if environment_ids is not UNSET:
            field_dict["environment_ids"] = environment_ids
        if plan_name is not UNSET:
            field_dict["plan_name"] = plan_name
        if current_period_start is not UNSET:
            field_dict["current_period_start"] = current_period_start
        if current_period_end is not UNSET:
            field_dict["current_period_end"] = current_period_end
        if entitlements is not UNSET:
            field_dict["entitlements"] = entitlements

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entitlement_response import EntitlementResponse

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        stripe_subscription_id = d.pop("stripe_subscription_id")

        status = d.pop("status")

        _environment_ids = d.pop("environment_ids", UNSET)
        environment_ids: list[UUID] | Unset = UNSET
        if _environment_ids is not UNSET:
            environment_ids = []
            for environment_ids_item_data in _environment_ids:
                environment_ids_item = UUID(environment_ids_item_data)

                environment_ids.append(environment_ids_item)

        def _parse_plan_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        plan_name = _parse_plan_name(d.pop("plan_name", UNSET))

        def _parse_current_period_start(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        current_period_start = _parse_current_period_start(d.pop("current_period_start", UNSET))

        def _parse_current_period_end(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        current_period_end = _parse_current_period_end(d.pop("current_period_end", UNSET))

        _entitlements = d.pop("entitlements", UNSET)
        entitlements: list[EntitlementResponse] | Unset = UNSET
        if _entitlements is not UNSET:
            entitlements = []
            for entitlements_item_data in _entitlements:
                entitlements_item = EntitlementResponse.from_dict(entitlements_item_data)

                entitlements.append(entitlements_item)

        subscription_response = cls(
            id=id,
            stripe_subscription_id=stripe_subscription_id,
            status=status,
            environment_ids=environment_ids,
            plan_name=plan_name,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
            entitlements=entitlements,
        )

        subscription_response.additional_properties = d
        return subscription_response

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
