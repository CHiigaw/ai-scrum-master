from fastapi import FastAPI
from app.slack_handler import slack_runner
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("🚀 Launching Slack bot in background...")
    asyncio.create_task(slack_runner())  # non-blocking


@app.get("/")
async def health_check():
    return {"status": "Bot is running 🚀"}


# To test if users are detected dynamically
from app.slack_utils import get_active_human_users

@app.get("/team")
def get_team_members():
    return get_active_human_users()

