import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import requests

app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("📈 Stock Sentiment Dashboard",
            style={"textAlign": "center", "color": "#00ff88"}),

    html.Div([
        dcc.Input(
            id="stock-input",
            type="text",
            placeholder="Enter symbol (AAPL, TSLA, GOOGL...)",
            debounce=True,
            style={
                "width": "300px",
                "padding": "10px",
                "fontSize": "16px",
                "borderRadius": "8px"
            }
        ),
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    html.Div(id="stock-cards", style={"textAlign": "center"}),
    dcc.Graph(id="price-chart"),
    html.Div(id="news-section", style={"padding": "20px"})

], style={
    "backgroundColor": "#1a1a2e",
    "minHeight": "100vh",
    "color": "white",
    "fontFamily": "Arial"
})


@app.callback(
    [Output("stock-cards", "children"),
     Output("price-chart", "figure"),
     Output("news-section", "children")],
    [Input("stock-input", "value")]
)
def update_dashboard(symbol):
    if not symbol:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            paper_bgcolor="#1a1a2e",
            plot_bgcolor="#1a1a2e"
        )
        return "", empty_fig, ""

    try:
        response = requests.get(f"http://127.0.0.1:8000/analyze/{symbol}")
        data = response.json()

        cards = html.Div([
            html.Div([
                html.H2(f"${data['price']}"),
                html.P(f"{data['symbol']} Stock Price")
            ], style={
                "display": "inline-block",
                "backgroundColor": "#16213e",
                "padding": "20px 40px",
                "borderRadius": "12px",
                "margin": "10px"
            }),
            html.Div([
                html.H2(data['sentiment']),
                html.P(f"Score: {data['sentiment_score']}")
            ], style={
                "display": "inline-block",
                "backgroundColor": "#16213e",
                "padding": "20px 40px",
                "borderRadius": "12px",
                "margin": "10px"
            }),
            html.Div([
                html.H2(data['recommendation']),
                html.P("Recommendation")
            ], style={
                "display": "inline-block",
                "backgroundColor": "#16213e",
                "padding": "20px 40px",
                "borderRadius": "12px",
                "margin": "10px"
            }),
        ])

        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name=symbol
        ))
        fig.update_layout(
            title=f"{symbol.upper()} - Last 30 Days",
            paper_bgcolor="#1a1a2e",
            plot_bgcolor="#1a1a2e",
            font=dict(color="white"),
            xaxis_rangeslider_visible=False
        )

        news_items = [html.H3("📰 Latest News")]
        for article in data['news']:
            color = "#00ff88" if article['score'] > 0 else "#ff4444" if article['score'] < 0 else "white"
            news_items.append(
                html.Div([
                    html.P(article['title'], style={"color": color}),
                    html.P(f"Sentiment Score: {article['score']}",
                           style={"color": "gray", "fontSize": "12px"})
                ], style={
                    "backgroundColor": "#16213e",
                    "padding": "15px",
                    "borderRadius": "8px",
                    "marginBottom": "10px"
                })
            )

        return cards, fig, html.Div(news_items)

    except Exception as e:
        return html.P(f"Error: {str(e)}"), go.Figure(), ""


if __name__ == "__main__":
    app.run(debug=True, port=8050)