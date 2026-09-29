from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .database import init_db
from .routes import router

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

s=get_settings()
app=FastAPI(title=s.app_name,version="1.0.0",debug=s.debug,lifespan=lifespan)
app.mount("/static",StaticFiles(directory="static"),name="static")
app.include_router(router)

@app.get("/health")
def health():
    return {"status":"ok","app":s.app_name,"gemini_configured":bool(s.gemini_api_key),"workout_model":s.gemini_workout_model,"tip_model":s.gemini_tip_model}
