from asyncio import Queue
import asyncio

try:
    from asyncio import QueueShutDown  # py3.13+
    HAVE_SHUTDOWN = True
except Exception:  # py3.11/3.12
    HAVE_SHUTDOWN = False
    class QueueShutDown(Exception):  # local shim so except blocks still work
        pass

SENTINEL = object()

def queue_shutdown(q: Queue, immediate: bool = False):
    if HAVE_SHUTDOWN:
        q.shutdown(immediate=immediate)
    else:
        # emulate shutdown
        if immediate:
            try:
                while True:
                    q.get_nowait()
            except asyncio.QueueEmpty:
                pass
        # push sentinel so consumers stop
        try:
            q.put_nowait(SENTINEL)
        except Exception:
            pass
