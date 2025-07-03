import subprocess
import httpx
import time

# Start Ollama if it's not already running
def start_ollama():
    try:
        httpx.get("http://localhost:11434", timeout=1.0)
        print("✅ Ollama already running.")
    except:
        print("⏳ Starting Ollama...")
        subprocess.Popen(["ollama", "run", "llama3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(10)
        print("✅ Ollama launched.")

start_ollama()

async def get_ai_reply(prompt: str) -> str:
    system_prompt = (
        "You are an AI Scrum Master in a Slack workspace. "
        "Your role is to collect updates, unblock the team, and keep communication focused. "
        "Keep your answers concise and professional. "
        "Avoid vague chit-chat or philosophical talk. "
        "Do not explain what a language model is. "
        "If someone says 'hi', respond with something like: 'Hey! Ready to give your daily update?'"
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": f"{system_prompt}\n\nUser: {prompt}\nAI:",
                    "stream": False
                }
            )
            return response.json().get("response", "⚠️ No response from AI.")
    except Exception as e:
        return f"⚠️ Failed to reply: {e}"


