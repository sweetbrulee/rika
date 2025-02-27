from typing import Coroutine, Callable, Any
import datetime
import asyncio


class Event:
    def __init__(
        self,
        time: datetime.datetime,
        coro_func: Callable[..., Coroutine],
        args: tuple = None,
        kwargs: dict = None,
    ):
        self.time = time
        self.coro_func = coro_func
        self.args = args if args is not None else ()
        self.kwargs = kwargs if kwargs is not None else {}


class Scheduler:
    _events: list[Event] = []
    _tasks: set[asyncio.Task] = set()

    @classmethod
    async def schedule(cls):
        """Don't forget to call this method to start the scheduler."""
        for event in cls._events:
            # Create a task for each event
            task = asyncio.create_task(cls._run_event(event))
            cls._tasks.add(task)
            # Automatically remove the task from the set when it's done
            task.add_done_callback(cls._tasks.discard)

        print(f"Scheduler scheduled {len(cls._events)} events.")

    @classmethod
    async def wait_for_all(cls):
        # Wait for all scheduled tasks to complete
        if cls._tasks:
            await asyncio.wait(cls._tasks)

    @classmethod
    async def _run_event(cls, event: Event):
        # Calculate the delay until the event's datetime
        delay = (
            event.time - datetime.datetime.now(datetime.timezone.utc)
        ).total_seconds()
        # Execute only if the delay is positive (negative delay has the danger of executing the event in the past)
        if delay < 0:
            return
        # Wait until the event's scheduled time
        await asyncio.sleep(delay)
        # Execute the coroutine function with the stored arguments
        try:
            coro = event.coro_func(*event.args, **event.kwargs)
            await coro
        except Exception as e:
            print(f"An error occurred in event scheduled at {event.time}: {e}")


def event(time: datetime.datetime, *d_args, **d_kwargs):
    """
    A decorator to schedule an event at a specific datetime.

    :param datetime: The datetime when the event should be executed.
    :param d_args: Positional arguments to pass to the coroutine function.
    :param d_kwargs: Keyword arguments to pass to the coroutine function.
    """

    def decorator(coro_func: Callable[..., Coroutine]):
        # Store the coroutine function and its arguments in the Scheduler
        Scheduler._events.append(Event(time, coro_func, d_args, d_kwargs))
        return coro_func  # Return the function unchanged

    return decorator
