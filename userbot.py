from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
group_ids = [
    int(os.getenv("GROUP_ID_1")),
    int(os.getenv("GROUP_ID_2")),
    int(os.getenv("GROUP_ID_3"))
]
channels = [
    {"username": os.getenv("CHANNEL_1"), "link": f"https://t.me/{os.getenv('CHANNEL_1')}", "label": " Sing Trending"},
    {"username": os.getenv("CHANNEL_2"), "link": f"https://t.me/{os.getenv('CHANNEL_2')}", "label": " Sing Raid Trending"},
]

client = TelegramClient("session_userbot", api_id, api_hash)

async def is_user_following(client, channel, user_id):
    try:
        await client(GetParticipantRequest(channel=channel["username"], participant=user_id))
        return True
    except UserNotParticipantError:
        return False
    except Exception as e:
        print(f"⚠️ Error checking {channel['username']}: {e}")
        return False

@client.on(events.ChatAction)
async def handler(event):
    if not (event.user_joined or event.user_added):
        return
    if event.chat_id not in group_ids:
        return

    user = await event.get_user()
    username = user.username or f"id{user.id}"
    print(f"🕵️ Checking @{username}...")

    links_text = "\n".join(
        f"👉 [{chan['label']}]({chan['link']})" for chan in channels
    )
    await client.send_message(
        event.chat_id,
        f"👋 Welcome @{username}!\n\n"
        f"⚠️ To stay in this group, you must join both official channels below.\n"
        f"⏳ You have 2 minutes to complete this or you will be removed.\n\n"
        f"{links_text}",
        link_preview=False,
        parse_mode="md"
    )

    await asyncio.sleep(120)

    still_missing = [chan["username"] for chan in channels if not await is_user_following(client, chan, user.id)]
    if still_missing:
        await client.kick_participant(event.chat_id, user.id)
        print(f"❌ @{username} removed for not joining: {still_missing}")
    else:
        print(f"✅ @{username} passed all channel checks.")

client.start()
print("✅ Userbot is running. Watching for new members...")
client.run_until_disconnected()
