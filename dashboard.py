import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import yfinance as yf
import requests

app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("📈 Stock Sentiment Dashboard",
            style={"textAlign": "center", "color": "#00ff88",
                   "paddingTop": "20px"}),

    html.Div([
        dcc.Input(
            id="stock-input",
            type="text",
            placeholder="AAPL, TSLA, GOOGL",
            style={
                "width": "400px",
                "padding": "10px",
                "fontSize": "16px",
                "borderRadius": "8px",
                "marginRight": "10px",
                "backgroundColor": "white",
                "color": "black"
            }
        ),
        html.Button(
            "Search 🔍",
            id="search-btn",
            n_clicks=0,
            style={
                "padding": "10px 20px",
                "fontSize": "16px",
                "borderRadius": "8px",
                "backgroundColor": "#00ff88",
                "border": "none",
                "cursor": "pointer",
                "fontWeight": "bold"
            }
        )
    ], style={"textAlign": "center", "marginBottom": "30px"}),

    html.Div(id="comparison-cards",
             style={"textAlign": "center", "marginBottom": "20px"}),

    dcc.Graph(id="comparison-chart"),
    dcc.Graph(id="sentiment-chart"),
    html.Div(id="news-section", style={"padding": "20px"})

], style={
    "backgroundColor": "#1a1a2e",
    "minHeight": "100vh",
    "color": "white",
    "fontFamily": "Arial"
})


@app.callback(
    [Output("comparison-cards", "children"),
     Output("comparison-chart", "figure"),
     Output("sentiment-chart", "figure"),
     Output("news-section", "children")],
    [Input("search-btn", "n_clicks")],
    [State("stock-input", "value")]
)
def update_dashboard(n_clicks, symbols_input):
    empty_fig = go.Figure()
    empty_fig.update_layout(
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e"
    )

    if not n_clicks or not symbols_input:
        return "", empty_fig, empty_fig, ""

    # Fix common symbol mistakes
    symbol_fixes = {
        "GOOGLE": "GOOGL",
        "ALPHABET": "GOOGL",
        "AMAZON": "AMZN",
        "MICROSOFT": "MSFT",
        "APPLE": "AAPL",
        "TESLA": "TSLA",
        "NETFLIX": "NFLX"
    }

    symbols = []
    for s in symbols_input.split(","):
        s = s.strip().upper()
        s = symbol_fixes.get(s, s)
        if s:
            symbols.append(s)

    all_data = []

    for symbol in symbols:
        try:
            response = requests.get(
                f"http://127.0.0.1:8000/analyze/{symbol}",
                timeout=10
            )
            data = response.json()
            if "error" not in data:
                all_data.append(data)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    if not all_data:
        return html.P("No data found!",
                      style={"color": "red"}), empty_fig, empty_fig, ""

    # Cards
    cards = []
    for stock in all_data:
        rec = stock['recommendation']
        border_color = "#00ff88" if "BUY" in rec else "#ff4444" if "SELL" in rec else "#ffaa00"
        cards.append(
            html.Div([
                html.H2(stock['symbol'],
                        style={"color": "#00ff88", "margin": "0"}),
                html.H3(f"${stock['price']}",
                        style={"margin": "5px 0"}),
                html.P(stock['sentiment'],
                       style={"margin": "5px 0"}),
                html.P(stock['recommendation'],
                       style={"margin": "5px 0", "fontWeight": "bold"}),
            ], style={
                "display": "inline-block",
                "backgroundColor": "#16213e",
                "padding": "20px 30px",
                "borderRadius": "12px",
                "margin": "10px",
                "minWidth": "150px",
                "border": f"2px solid {border_color}"
            })
        )

    # Candlestick chart
    price_fig = go.Figure()
    for stock in all_data:
        try:
            ticker = yf.Ticker(stock['symbol'])
            hist = ticker.history(period="1mo")
            price_fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name=stock['symbol'],
                increasing_line_color="#00ff88",
                decreasing_line_color="#ff4444"
            ))
        except:
            pass

    price_fig.update_layout(
        title="📊 Candlestick Chart - Last 30 Days",
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e",
        font=dict(color="white"),
        legend=dict(bgcolor="#16213e"),
        xaxis_rangeslider_visible=False
    )

    # Sentiment chart
    sentiment_fig = go.Figure()
    sentiment_fig.add_trace(go.Bar(
        x=[s['symbol'] for s in all_data],
        y=[s['sentiment_score'] for s in all_data],
        marker_color=[
            "#00ff88" if s['sentiment_score'] > 0.1
            else "#ff4444" if s['sentiment_score'] < -0.1
            else "#ffaa00"
            for s in all_data
        ],
        text=[s['sentiment_score'] for s in all_data],
        textposition='auto'
    ))
    sentiment_fig.update_layout(
        title="🧠 Sentiment Comparison",
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e",
        font=dict(color="white")
    )

    # News
    news_items = []
    for stock in all_data:
        news_items.append(html.H3(f"📰 {stock['symbol']} Latest News",
                                  style={"color": "#00ff88"}))
        for article in stock['news']:
            color = "#00ff88" if article['score'] > 0 \
                else "#ff4444" if article['score'] < 0 else "white"
            news_items.append(
                html.Div([
                    html.P(article['title'],
                           style={"color": color}),
                    html.P(f"Sentiment Score: {article['score']}",
                           style={"color": "gray", "fontSize": "12px"})
                ], style={
                    "backgroundColor": "#16213e",
                    "padding": "15px",
                    "borderRadius": "8px",
                    "marginBottom": "10px"
                })
            )

    return html.Div(cards), price_fig, sentiment_fig, html.Div(news_items)


if __name__ == "__main__":
    app.run(debug=True, port=8050)