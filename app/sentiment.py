from textblob import TextBlob
import yfinance as yf

def analyze_sentiment(symbol: str):
    ticker = yf.Ticker(symbol)
    
    # Get latest news
    news = ticker.news
    
    if not news:
        return {"sentiment": "neutral", "score": 0}
    
    total_score = 0
    analyzed = []
    
    for article in news[:5]:
        # Try different ways to get title
        title = (
            article.get("title") or
            article.get("content", {}).get("title") or
            article.get("headline") or
            ""
        )
        
        if not title:
            continue
            
        # Analyze sentiment
        blob = TextBlob(title)
        score = blob.sentiment.polarity
        
        analyzed.append({
            "title": title,
            "score": round(score, 2)
        })
        
        total_score += score
    
    if not analyzed:
        return {
            "symbol": symbol.upper(),
            "sentiment": "NEUTRAL 😐",
            "score": 0,
            "message": "No news found"
        }
    
    avg_score = round(total_score / len(analyzed), 2)
    
    if avg_score > 0.1:
        sentiment = "POSITIVE 📈"
    elif avg_score < -0.1:
        sentiment = "NEGATIVE 📉"
    else:
        sentiment = "NEUTRAL 😐"
    
    return {
        "symbol": symbol.upper(),
        "sentiment": sentiment,
        "score": avg_score,
        "news_analyzed": analyzed
    }