from typing import Optional, Callable

from typing_extensions import TypeVar, TypedDict, Any, Awaitable

from starlette.websockets import WebSocket


from .message import Header, Payload, MessageData

UserHandlerParams = TypeVar("UserHandlerParams")

class HandlerResult(TypedDict, total=False):
    status: Optional[int]
    headers: Optional[Header]
    payload: Optional[Any]


AccessCheck = Callable[[WebSocket, MessageData], Awaitable[bool]]


HydrateFunction = Callable[[WebSocket,MessageData], Awaitable[UserHandlerParams]]
"""
if set its return value, will be passed as handler's single argument
"""

DehydrateFunction = Callable[[Any], Awaitable[Payload]]
"""
if set its return value, will be returned as payload to user
"""

class RouteOptions(TypedDict, total=False):
    access: Optional[AccessCheck]
    hydrate: Optional[HydrateFunction]
    dehydrate: Optional[DehydrateFunction]