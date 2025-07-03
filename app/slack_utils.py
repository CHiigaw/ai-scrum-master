from slack_sdk import WebClient
from app.config import SLACK_BOT_TOKEN

slack_client = WebClient(token=SLACK_BOT_TOKEN)

def get_active_human_users() -> list:
    users = []

    try:
        response = slack_client.users_list()

        if not response.get("ok"):
            print("❌ Slack API call failed:", response.get("error"))
            return []

        members = response.get("members", [])
        for member in members:
            if (
                not member.get("deleted") and
                not member.get("is_bot") and
                member.get("id") != "USLACKBOT"
            ):
                users.append({
                    "id": member["id"],
                    "name": member["real_name"]
                })

    except Exception as e:
        print(f"❌ Exception while fetching users: {e}")

    return users
