from typing import Dict, Any, Optional

from pydantic import BaseModel, Field, AliasChoices

Header = Dict[str, Any]
Payload = bool | int | float | list | str | Dict


class MessageData(BaseModel):
    headers: Optional[Header]
    payload: Optional[Payload]

    def get_data(self):
        return {'headers': self.headers or {}, 'payload': self.payload or {}}


class Request(MessageData):
    track_id: str | int = Field(validation_alias=AliasChoices('track_id', 'uuid'), serialization_alias='uuid')
    path: str = Field(validation_alias=AliasChoices('path', 'route'), serialization_alias='route')


class Response(MessageData):
    track_id: str | int = Field(validation_alias=AliasChoices('track_id', 'uuid'), serialization_alias='uuid')
    status: int
