import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

load_dotenv()

from app.services.database import init_db
from app.services.telegram import set_webhook
from app.handlers.message import handle_message

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        result = await set_webhook(f"{webhook_url}/webhook")
        print(f"Webhook set: {result}")
    else:
        print("⚠️  WEBHOOK_URL not set — run set_webhook() manually or use polling.")
    yield
    # Shutdown (nothing to clean up)

app = FastAPI(
    title="HealthBot",
    description="Telegram health Q&A bot powered by Claude",
    lifespan=lifespan
)

@app.post("/webhook")
async def webhook(request: Request):
    """Receive updates from Telegram."""
    try:
        update = await request.json()
        await handle_message(update)
        return JSONResponse({"ok": True})
    except Exception as e:
        print(f"Error handling update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "bot": "HealthBot"}

@app.get("/")
async def root():
    return {"message": "HealthBot is running. Send messages via Telegram."}