from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routes import router

app = FastAPI(title="Stock Sentiment Dashboard")

app.include_router(router)

@app.get("/")
def home():
    return HTMLResponse("<h1>Stock Sentiment Dashboard is Running! 🚀</h1>")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Server is healthy"}