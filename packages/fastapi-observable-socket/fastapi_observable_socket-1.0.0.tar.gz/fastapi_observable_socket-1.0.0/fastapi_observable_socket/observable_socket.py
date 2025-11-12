import json
import logging
from asyncio import Queue, create_task, Task
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Callable, Dict

from pydantic import ValidationError
from starlette.websockets import WebSocket
from typing_extensions import Awaitable

from .compat import QueueShutDown, queue_shutdown
from .message import Request, Response, Header, Payload
from .response_sender import send_response
from .route_options import RouteOptions, HydrateFunction, DehydrateFunction, AccessCheck, HandlerResult, \
    UserHandlerParams
from .status import Status

# function types

SocketAccess = Callable[[WebSocket], Awaitable[bool]]
"""
Socket Access function can use websocket.headers or websocket.scope to check if connection is allowed or not.
"""

Handler = Callable[[UserHandlerParams], Awaitable[HandlerResult]] | Callable[
    [WebSocket, Header, Payload], Awaitable[HandlerResult]]
"""
If user doesn't set a hydration for the route, then WebSocket, Headers and Payload will be sent to handler function.
Else if the user provide the hydration for the route then the output of hydration function will be sent to handler function.
"""

logger = logging.getLogger(__name__)



@dataclass
class Route:
    handler: Handler
    options: RouteOptions | None = None


class SocketRouter:
    def __init__(self, access_logic: SocketAccess | None = None):
        self._routes: Dict[str, Route] = {}
        self._access_logic = access_logic

    # using route decorator a function can simply be used as route handler for path
    def route(self, path: str, options: RouteOptions | None = None):
        def deco(fn: Handler):
            route = Route(fn, options)
            self._routes[path] = route
            return fn

        return deco

    # fastapi expect Callable[[WebSocket], Awaitable[None]] for websocket
    async def __call__(self, ws: WebSocket):
        # check if opening websocket is allowed at first place
        access_granted = True
        if self._access_logic:
            access_granted = await self._access_logic(ws)
        if access_granted:
            await ws.accept()
            # now that socket has been accepted, send_task should be started
            response_queue = Queue()
            response_task: Task = create_task(send_response(ws, response_queue))
            current_track_id = 0

            try:
                while True:
                    request_text = await ws.receive_text()

                    payload = {"Message": "Illegal Request Format"}
                    try:
                        envelope = json.loads(request_text)
                    except JSONDecodeError:
                        # the format is not even json parsable, so respond as error
                        response = Response(
                            track_id=0,
                            status=Status.BAD_REQUEST,
                            headers=None,
                            payload=payload
                        ).model_dump(by_alias=True)
                        await response_queue.put(response)
                        continue

                    try:
                        request = Request.model_validate(envelope)
                    except ValidationError:
                        # the format is not valid Request, yet it might be heartbit PING or carry a track_id
                        path = envelope.get("path", envelope.get("route"))
                        if path == 'PING':
                            response = Request(
                                track_id=0,
                                path="PONG",
                                headers=None,
                                payload=None
                            ).model_dump(by_alias=True)
                            await response_queue.put(response)
                            continue

                        track_id = envelope.get("track_id", 0)
                        response = Response(
                            track_id=track_id,
                            status=Status.BAD_REQUEST,
                            headers=None,
                            payload=payload
                        ).model_dump(by_alias=True)
                        await response_queue.put(response)
                        continue

                    track_id = request.track_id
                    current_track_id = track_id
                    path = request.path

                    if path == 'PING':
                        response = Request(
                            track_id=track_id,
                            path="PONG",
                            headers=None,
                            payload=None
                        ).model_dump(by_alias=True)
                        await response_queue.put(response)
                        continue

                    route: Route | None = self._routes.get(path)
                    if not route:
                        response = Response(
                            track_id=track_id,
                            status=Status.NOT_FOUND,
                            headers=None,
                            payload={"Message": "Path not found"}
                        ).model_dump(by_alias=True)
                        await response_queue.put(response)
                        continue

                    response = await process_request(ws, request, route)
                    await response_queue.put(response)

            except Exception as e:
                logger.error(e)
                response = Response(
                    track_id=current_track_id,
                    status=Status.INTERNAL_SERVER_ERROR,
                    headers=None,
                    payload={"Message": "Internal Server Error"}
                ).model_dump(by_alias=True)
                try:
                    await response_queue.put(response)
                except QueueShutDown:
                    response_task.cancel()
            finally:
                queue_shutdown(response_queue) # prevents further puts but gets are still welcome
                try:
                    await response_queue.join() # try to send any remained responses
                except RuntimeError:
                    pass

        else:
            await ws.close(code=1008, reason="Access denied")


async def process_request(ws: WebSocket, request: Request, route: Route):
    options: RouteOptions = route.options or {}
    message_data = request.get_data()
    track_id = request.track_id

    try:
        # first checks if user can call path with posted data (Content Access or similar checks)
        access_check: AccessCheck | None = options.get('access')
        if access_check is not None:
            if not await access_check(ws, message_data):
                return Response(
                    track_id=track_id,
                    status=Status.FORBIDDEN,
                    headers=None,
                    payload={"Message": "Access denied"}
                ).model_dump(by_alias=True)

        hydrate: HydrateFunction | None = options.get('hydrate', None)
        if hydrate is not None:
            hydrated = await hydrate(ws, message_data)
            result = await route.handler(hydrated)
        else:
            payload: Payload = message_data.payload
            headers: Header = request.headers or {}
            result = await route.handler(ws, headers, payload)

        status = result.get('status', Status.OK)
        out_headers: Header = result.get('headers', {})
        out_payload = result.get('payload')

        dehydrate: DehydrateFunction | None = options.get('dehydrate', None)
        if dehydrate is not None and 200 <= status < 300:
            out_payload = await dehydrate(out_payload)

        return Response(
            track_id=track_id,
            status=status,
            headers=out_headers,
            payload=out_payload
        ).model_dump(by_alias=True)

    except Exception as e:
        logger.error(e)
        return Response(
            track_id=track_id,
            status=Status.INTERNAL_SERVER_ERROR,
            headers=None,
            payload={"Message": "Internal Server Error"}
        ).model_dump(by_alias=True)
