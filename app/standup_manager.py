# app/standup_manager.py

from app.slack_utils import slack_client, get_active_human_users
from app.summarizer import get_ai_reply
from app.config import CHANNEL_ID
import asyncio

# State: user_id → current index + answers
standup_state = {}  # { user_id: { 'name': str, 'answers': list, 'index': int } }

STANDUP_QUESTIONS = [
    "👨‍💻 What did you work on yesterday?",
    "📅 What are you planning to do today?",
    "⛔ Are there any blockers?"
]

# 🔁 Send first question to each user and start tracking
async def run_standup():
    users = get_active_human_users()
    standup_state.clear()

    for user in users:
        user_id = user["id"]
        standup_state[user_id] = {
            "name": user["name"],
            "answers": [],
            "index": 0
        }

        try:
            slack_client.chat_postMessage(channel=user_id, text="👋 Hey! Time for your daily standup.")
            await asyncio.sleep(0.5)
            slack_client.chat_postMessage(channel=user_id, text=STANDUP_QUESTIONS[0])
        except Exception as e:
            print(f"❌ Failed to DM {user['name']}: {e}")

# ✉️ Called from slack_handler when user replies
async def handle_user_reply(user_id: str, message: str):
    if user_id not in standup_state:
        print(f"⚠️ Received message from {user_id} but they're not in standup_state.")
        return

    user = standup_state[user_id]
    user["answers"].append(message)
    user["index"] += 1

    if user["index"] < len(STANDUP_QUESTIONS):
        next_question = STANDUP_QUESTIONS[user["index"]]
        slack_client.chat_postMessage(channel=user_id, text=next_question)
    else:
        slack_client.chat_postMessage(channel=user_id, text="✅ Thanks! I’ve got your full update.")
        await check_if_all_done()

# ✅ Check if everyone is finished
async def check_if_all_done():
    for user in standup_state.values():
        if len(user["answers"]) < len(STANDUP_QUESTIONS):
            return  # Someone’s not done yet

    print("✅ All users responded. Posting summary...")
    await summarize_and_post()

# 🧠 Ask LLM to summarize all responses and post to channel
async def summarize_and_post():
    formatted = ""

    for user_id, data in standup_state.items():
        name = data["name"]
        answers = data["answers"]
        formatted += f"*{name}*\n"
        for q, a in zip(STANDUP_QUESTIONS, answers):
            formatted += f"{q}\n➡️ {a}\n"
        formatted += "\n"

    summary_prompt = (
        "You are an AI Scrum Master. Summarize the following daily standup notes:\n\n" + formatted
    )

    summary = await get_ai_reply(summary_prompt)

    try:
        slack_client.chat_postMessage(channel=CHANNEL_ID, text=f"📋 *Daily Standup Summary*\n\n{summary}")
    except Exception as e:
        print(f"❌ Failed to post summary: {e}")
