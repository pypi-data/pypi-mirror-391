import logging
from asyncio import CancelledError, Queue

from starlette.websockets import WebSocketDisconnect, WebSocket

from .compat import QueueShutDown, SENTINEL, HAVE_SHUTDOWN

logger = logging.getLogger(__name__)

async def send_response(ws: WebSocket, q: Queue):
    try:
        while True:
            item = await q.get()
            if not HAVE_SHUTDOWN and item is SENTINEL:
                return
            await ws.send_json(item)
            q.task_done()
    except (QueueShutDown, WebSocketDisconnect, RuntimeError):
            pass
    except CancelledError:
        pass
    except Exception:
        logger.exception("send_response crashed")
    finally:
        raise RuntimeError("sending response is finished") # catch on queue.join()
