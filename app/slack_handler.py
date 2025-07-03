from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from app.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN
from app.summarizer import get_ai_reply
import re

def clean_message(text: str) -> str:
    return re.sub(r"<@U\w+>", "@user", text)


app = AsyncApp(token=SLACK_BOT_TOKEN)

@app.event("message")
async def handle_message_events(body, say, logger):
    print("📩 EVENT RECEIVED:")
    print(body)  # raw slack event body

    user = body["event"].get("user")
    text = body["event"].get("text")
    if user and text:
        print(f"User {user} said: {text}")
        prompt = clean_message(text)
        reply = await get_ai_reply(prompt)
        await say(f"<@{user}> {reply}")

@app.event("app_mention")
async def handle_app_mention_events(body, say, logger):
    user = body["event"].get("user")
    text = body["event"].get("text")
    logger.info(f"Mention from {user}: {text}")
    prompt = clean_message(text)
    reply = await get_ai_reply(prompt)
    await say(f"<@{user}> {reply}")


handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)

async def slack_runner():
    await handler.start_async()

