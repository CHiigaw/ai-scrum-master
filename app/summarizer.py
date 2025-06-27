import httpx

async def get_ai_reply(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False}
        )
        data = response.json()
        return data.get("response", "Sorry, I didn’t get that.")
