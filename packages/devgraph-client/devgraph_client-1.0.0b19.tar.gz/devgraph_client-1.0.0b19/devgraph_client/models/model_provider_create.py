from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.anthropic_model_provider_create import AnthropicModelProviderCreate
    from ..models.open_ai_model_provider_create import OpenAIModelProviderCreate
    from ..models.xai_model_provider_create import XAIModelProviderCreate


T = TypeVar("T", bound="ModelProviderCreate")


@_attrs_define
class ModelProviderCreate:
    """
    Attributes:
        data (AnthropicModelProviderCreate | OpenAIModelProviderCreate | XAIModelProviderCreate):
    """

    data: AnthropicModelProviderCreate | OpenAIModelProviderCreate | XAIModelProviderCreate
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.open_ai_model_provider_create import OpenAIModelProviderCreate
        from ..models.xai_model_provider_create import XAIModelProviderCreate

        data: dict[str, Any]
        if isinstance(self.data, OpenAIModelProviderCreate):
            data = self.data.to_dict()
        elif isinstance(self.data, XAIModelProviderCreate):
            data = self.data.to_dict()
        else:
            data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.anthropic_model_provider_create import AnthropicModelProviderCreate
        from ..models.open_ai_model_provider_create import OpenAIModelProviderCreate
        from ..models.xai_model_provider_create import XAIModelProviderCreate

        d = dict(src_dict)

        def _parse_data(
            data: object,
        ) -> AnthropicModelProviderCreate | OpenAIModelProviderCreate | XAIModelProviderCreate:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = OpenAIModelProviderCreate.from_dict(data)

                return data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_1 = XAIModelProviderCreate.from_dict(data)

                return data_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            data_type_2 = AnthropicModelProviderCreate.from_dict(data)

            return data_type_2

        data = _parse_data(d.pop("data"))

        model_provider_create = cls(
            data=data,
        )

        model_provider_create.additional_properties = d
        return model_provider_create

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
