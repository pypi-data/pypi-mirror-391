from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chat_message import ChatMessage
    from ..models.response_format import ResponseFormat


T = TypeVar("T", bound="ChatCompletionRequest")


@_attrs_define
class ChatCompletionRequest:
    """
    Attributes:
        model (str): The model to use, e.g., 'gpt-3.5-turbo' or 'gpt-4'
        messages (list[ChatMessage]): List of messages comprising the conversation
        temperature (float | None | Unset):
        max_tokens (int | None | Unset):
        stream (bool | None | Unset):
        n (int | None | Unset):
        response_format (ResponseFormat | Unset):
    """

    model: str
    messages: list[ChatMessage]
    temperature: float | None | Unset = UNSET
    max_tokens: int | None | Unset = UNSET
    stream: bool | None | Unset = UNSET
    n: int | None | Unset = UNSET
    response_format: ResponseFormat | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        model = self.model

        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        temperature: float | None | Unset
        if isinstance(self.temperature, Unset):
            temperature = UNSET
        else:
            temperature = self.temperature

        max_tokens: int | None | Unset
        if isinstance(self.max_tokens, Unset):
            max_tokens = UNSET
        else:
            max_tokens = self.max_tokens

        stream: bool | None | Unset
        if isinstance(self.stream, Unset):
            stream = UNSET
        else:
            stream = self.stream

        n: int | None | Unset
        if isinstance(self.n, Unset):
            n = UNSET
        else:
            n = self.n

        response_format: dict[str, Any] | Unset = UNSET
        if not isinstance(self.response_format, Unset):
            response_format = self.response_format.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model": model,
                "messages": messages,
            }
        )
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if stream is not UNSET:
            field_dict["stream"] = stream
        if n is not UNSET:
            field_dict["n"] = n
        if response_format is not UNSET:
            field_dict["response_format"] = response_format

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_message import ChatMessage
        from ..models.response_format import ResponseFormat

        d = dict(src_dict)
        model = d.pop("model")

        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = ChatMessage.from_dict(messages_item_data)

            messages.append(messages_item)

        def _parse_temperature(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        temperature = _parse_temperature(d.pop("temperature", UNSET))

        def _parse_max_tokens(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_tokens = _parse_max_tokens(d.pop("max_tokens", UNSET))

        def _parse_stream(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        stream = _parse_stream(d.pop("stream", UNSET))

        def _parse_n(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        n = _parse_n(d.pop("n", UNSET))

        _response_format = d.pop("response_format", UNSET)
        response_format: ResponseFormat | Unset
        if isinstance(_response_format, Unset):
            response_format = UNSET
        else:
            response_format = ResponseFormat.from_dict(_response_format)

        chat_completion_request = cls(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            n=n,
            response_format=response_format,
        )

        chat_completion_request.additional_properties = d
        return chat_completion_request

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
