import os
from bot import init_bot


def main():
    client = init_bot()
    from modules import events  # Do not delete this line

    client.run(os.getenv("RIKA_DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    main()
