import os
from groq import AsyncGroq

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# Best Groq model for health Q&A — fast and capable
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are HealthBot, a helpful and empathetic health information assistant on Telegram.

YOUR ROLE:
- Provide clear, accurate general health information and education
- Help users understand symptoms, conditions, medications, and healthy habits
- Offer guidance on when to seek professional medical care
- Support users in making informed decisions about their health

STRICT RULES — follow these without exception:
1. NEVER diagnose a condition. You can explain what symptoms may indicate, but never say "you have X".
2. NEVER prescribe or recommend specific medications or dosages.
3. ALWAYS recommend consulting a qualified doctor for personal medical concerns.
4. If a user expresses thoughts of self-harm or suicide, immediately respond with crisis resources and encourage them to call emergency services.
5. Keep responses concise and easy to understand — avoid heavy medical jargon.
6. If you're unsure about something, say so clearly rather than guessing.
7. If the user asks about anything unrelated to health, medicine, or wellness, 
   politely decline and remind them you are a health assistant only. 
   Do not answer questions about sports, politics, entertainment, or any 
   other non-health topic.

EMERGENCY DETECTION:
If the user mentions chest pain + shortness of breath, signs of stroke, severe bleeding, difficulty breathing, or suicidal ideation — immediately tell them to call emergency services (e.g. 112 or their local emergency number) before anything else.

TONE:
- Warm, calm, and supportive
- Non-judgmental
- Clear and plain language

END EVERY RESPONSE WITH:
A brief reminder like: "Remember, I'm an AI assistant — please consult a healthcare professional for personal medical advice."
"""

CRISIS_KEYWORDS = [
    "kill myself", "want to die", "suicide", "end my life",
    "self harm", "hurt myself", "no reason to live"
]

EMERGENCY_SYMPTOMS = [
    "chest pain", "can't breathe", "difficulty breathing",
    "stroke", "not breathing", "severe bleeding", "unconscious"
]

def detect_crisis(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in CRISIS_KEYWORDS)

def detect_emergency(text: str) -> bool:
    text_lower = text.lower()
    return any(sym in text_lower for sym in EMERGENCY_SYMPTOMS)

async def get_health_response(user_message: str, history: list) -> str:
    """Get a response from Groq with conversation history for context."""

    # Crisis check — override normal flow
    if detect_crisis(user_message):
        return (
            "🚨 I'm concerned about what you've shared. Please know you're not alone.\n\n"
            "*If you're in immediate danger, please call emergency services (112 or your local number) right away.*\n\n"
            "You can also reach out to a crisis helpline:\n"
            "• Nigeria: Suicide Prevention Initiative — 0800-800-SAFE\n"
            "• International: findahelpline.com\n\n"
            "Please talk to someone you trust or a mental health professional. 💙"
        )

    # Emergency symptom check
    emergency_prefix = ""
    if detect_emergency(user_message):
        emergency_prefix = (
            "⚠️ *Some symptoms you've described may require immediate medical attention.*\n"
            "If this is an emergency, please call 112 or go to the nearest hospital immediately.\n\n"
        )

    # Build messages with system prompt + history + new message
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + history
        + [{"role": "user", "content": user_message}]
    )

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1000,
        temperature=0.7,
    )

    reply = response.choices[0].message.content
    return emergency_prefix + reply