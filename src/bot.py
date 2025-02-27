from modules.prepare_env import client
from commands import music
from commands import gizmo
from commands import voice


def init_bot():
    cogs = [music, gizmo, voice]

    for cog in cogs:
        cog.setup(client)

    return client
