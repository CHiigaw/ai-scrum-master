from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from app.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN
from app.summarizer import get_ai_reply

app = AsyncApp(token=SLACK_BOT_TOKEN)

@app.event("message")
async def handle_message_events(body, say, logger):
    user = body["event"].get("user")
    text = body["event"].get("text")
    if user and text:
        logger.info(f"Message from {user}: {text}")
        reply = await get_ai_reply(text)
        await say(f"<@{user}> {reply}")

async def start_slack_bot():
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()
