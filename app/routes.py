from fastapi import APIRouter
import yfinance as yf
from app.sentiment import analyze_sentiment

router = APIRouter()

@router.get("/stock/{symbol}")
def get_stock(symbol: str):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    if data.empty:
        return {"error": "Stock not found"}
    current_price = round(data["Close"].iloc[-1], 2)
    return {
        "symbol": symbol.upper(),
        "price": current_price,
        "currency": "USD"
    }

@router.get("/sentiment/{symbol}")
def get_sentiment(symbol: str):
    result = analyze_sentiment(symbol)
    return result

@router.get("/analyze/{symbol}")
def analyze_stock(symbol: str):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    if data.empty:
        return {"error": "Stock not found"}
    current_price = round(data["Close"].iloc[-1], 2)
    sentiment_data = analyze_sentiment(symbol)
    return {
        "symbol": symbol.upper(),
        "price": current_price,
        "currency": "USD",
        "sentiment": sentiment_data["sentiment"],
        "sentiment_score": sentiment_data["score"],
        "news": sentiment_data["news_analyzed"],
        "recommendation": get_recommendation(sentiment_data["score"])
    }

def get_recommendation(score: float):
    if score > 0.1:
        return "BUY 🟢"
    elif score < -0.1:
        return "SELL 🔴"
    else:
        return "HOLD 🟡"