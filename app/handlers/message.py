from app.services import database, ai, telegram

HELP_TEXT = """
👋 *Welcome to HealthBot!*

I can help you with:
• General health questions
• Understanding symptoms
• Healthy lifestyle tips
• When to see a doctor

*Commands:*
/start — Welcome message
/help — Show this menu
/clear — Clear your conversation history
/disclaimer — View full medical disclaimer

Just type your health question and I'll do my best to help! 🏥

_Remember: I'm an AI assistant, not a doctor. Always consult a healthcare professional for medical advice._
"""

DISCLAIMER_TEXT = """
⚕️ *Medical Disclaimer*

HealthBot is an AI-powered health information service. It is:

✅ Designed to provide general health education
✅ A tool to help you understand health topics
✅ A guide on when to seek professional care

❌ NOT a substitute for professional medical advice
❌ NOT able to diagnose conditions
❌ NOT able to prescribe medication
❌ NOT a licensed medical professional

*In an emergency, always call 112 or your local emergency number.*

By using HealthBot, you acknowledge that all information provided is for educational purposes only.
"""

async def handle_message(update: dict):
    """Main entry point for all incoming Telegram updates."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    user = message.get("from", {})
    user_id = user.get("id", chat_id)
    username = user.get("username", "")
    first_name = user.get("first_name", "User")
    text = message.get("text", "").strip()

    if not text:
        await telegram.send_message(chat_id, "Please send a text message. I can't process other file types yet.")
        return

    # Register or update user
    await database.upsert_user(user_id, username, first_name)

    # Handle commands
    if text.startswith("/start"):
        await telegram.send_message(chat_id, f"Hello {first_name}! 👋\n\n" + HELP_TEXT)
        return

    if text.startswith("/help"):
        await telegram.send_message(chat_id, HELP_TEXT)
        return

    if text.startswith("/disclaimer"):
        await telegram.send_message(chat_id, DISCLAIMER_TEXT)
        return

    if text.startswith("/clear"):
        await database.clear_history(user_id)
        await telegram.send_message(chat_id, "✅ Your conversation history has been cleared.")
        return

    # Show typing indicator
    await telegram.send_typing(chat_id)

    # Fetch history for context
    history = await database.get_conversation_history(user_id, limit=10)

    # Get AI response
    reply = await ai.get_health_response(text, history)

    # Save both sides of the conversation
    await database.save_message(user_id, "user", text)
    await database.save_message(user_id, "assistant", reply)

    # Send reply
    await telegram.send_message(chat_id, reply)