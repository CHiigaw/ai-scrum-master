from fastapi import FastAPI
from app.slack_handler import start_slack_bot

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await start_slack_bot()

@app.get("/")
async def health_check():
    return {"status": "Bot is running 🚀"}
