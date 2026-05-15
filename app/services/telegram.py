import os
import httpx

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

def _url(method: str) -> str:
    return TELEGRAM_API.format(token=os.getenv("TELEGRAM_BOT_TOKEN"), method=method)

async def send_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """Send a text message to a Telegram chat."""
    async with httpx.AsyncClient() as client:
        await client.post(_url("sendMessage"), json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        })

async def send_typing(chat_id: int):
    """Show 'typing...' indicator while processing."""
    async with httpx.AsyncClient() as client:
        await client.post(_url("sendChatAction"), json={
            "chat_id": chat_id,
            "action": "typing"
        })

async def set_webhook(webhook_url: str):
    """Register the webhook with Telegram."""
    async with httpx.AsyncClient() as client:
        response = await client.post(_url("setWebhook"), json={"url": webhook_url})
        return response.json()

async def delete_webhook():
    """Remove the webhook (useful for switching to polling)."""
    async with httpx.AsyncClient() as client:
        response = await client.post(_url("deleteWebhook"))
        return response.json()