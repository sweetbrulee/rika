import asyncio
import itertools
from typing import Any, Callable
import discord
from discord.utils import Values, AutocompleteFunc, V


def autocomplete(values: Values) -> AutocompleteFunc:
    return basic_autocomplete(values, filter=lambda c, i: True)


# You don't need this modified version after pycord v2.7,
# because I have already PR this modification to pycord repo (v2.7) and they accepted it.
def basic_autocomplete(
    values: Values, *, filter: Callable | None = None
) -> AutocompleteFunc:

    async def autocomplete_callback(ctx: discord.AutocompleteContext) -> V:
        _values = values  # since we reassign later, python considers it local if we don't do this

        if callable(_values):
            _values = _values(ctx)
        if asyncio.iscoroutine(_values):
            _values = await _values

        if filter is None:

            def _filter(ctx: discord.AutocompleteContext, item: Any) -> bool:
                item = getattr(item, "name", item)
                return str(item).lower().startswith(str(ctx.value or "").lower())

            gen = (val for val in _values if _filter(ctx, val))

        elif asyncio.iscoroutinefunction(filter):
            gen = (val for val in _values if await filter(ctx, val))

        elif callable(filter):
            gen = (val for val in _values if filter(ctx, val))

        else:
            raise TypeError("``filter`` must be callable.")

        return iter(itertools.islice(gen, 25))

    return autocomplete_callback
