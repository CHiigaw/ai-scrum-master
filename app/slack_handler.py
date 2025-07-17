from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from app.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN
from app.summarizer import get_ai_reply
from app.standup_manager import handle_user_reply, run_standup  # ✭ added run_standup
import re

app = AsyncApp(token=SLACK_BOT_TOKEN)

# Clean text to remove user mentions (e.g. <@U123>)
def clean_message(text: str) -> str:
    return re.sub(r"<@U\\w+>", "@user", text)

@app.command("/start-standup")
async def command_start_standup(ack, respond, body):
    await ack()
    user = body.get("user_id")
    await respond(f"👋 Starting the standup! Thanks <@{user}>.")
    await run_standup()

@app.event("message")
async def handle_message_events(body, say, logger):
    print("📩 EVENT RECEIVED:")
    print(body)

    event = body.get("event", {})
    user_id = event.get("user")
    text = event.get("text")
    channel_type = event.get("channel_type")

    if not user_id or not text:
        return

    # 📬 Handle direct messages (private standup responses)
    if channel_type == "im":
        print(f"✏️ DM from {user_id}: {text}")
        await handle_user_reply(user_id, text)
        return

    # 💬 For public messages in channels (fallback LLM reply)
    prompt = clean_message(text)
    reply = await get_ai_reply(prompt)
    await say(f"<@{user_id}> {reply}")

@app.event("app_mention")
async def handle_app_mention_events(body, say, logger):
    user = body["event"].get("user")
    text = body["event"].get("text")
    logger.info(f"Mention from {user}: {text}")

    prompt = clean_message(text)
    reply = await get_ai_reply(prompt)
    await say(f"<@{user}> {reply}")

# Socket mode runner
handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)

async def slack_runner():
    await handler.start_async()
