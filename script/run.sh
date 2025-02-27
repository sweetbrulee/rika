if [ "$RIKA_DISCORD_BOT_TYPE" = "production" ] # Production bot
then
    echo "Starting production bot"
    fastapi run src/backend/app.py --port $PORT & python3 ./src/main.py
elif [ "$RIKA_DISCORD_BOT_TYPE" = "staged" ] # Staged bot
then
    echo "Starting staged bot"
    fastapi run src/backend/app.py --port $PORT & python3 ./src/main.py
else
    echo "Unknown bot type"
    exit 1
fi