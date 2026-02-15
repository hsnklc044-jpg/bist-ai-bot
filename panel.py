from flask import Flask, request, Response
import pandas as pd
import yfinance as yf
import os

app = Flask(__name__)

USERNAME = os.getenv("PANEL_USER", "admin")
PASSWORD = os.getenv("PANEL_PASS", "1234")

HISSELER = ["ASELS.IS","TUPRS.IS","KCHOL.IS","SISE.IS","YKBNK.IS","AKBNK.IS","BIMAS.IS","THYAO.IS"]


def check_auth(username, password):
    return username == USERNAME and password == PASSWORD


def authenticate():
    return Response(
        "Giriş gerekli", 401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated


@app.route("/")
@requires_auth
def panel():
    data = yf.download(HISSELER, period="1y")["Close"]

    returns = data.pct_change().dropna()
    portfoy = returns.mean(axis=1).cumsum()

    toplam_getiri = round(portfoy.iloc[-1] * 100, 2)
    sharpe = round((returns.mean().mean() / returns.std().mean()) * (252 ** 0.5), 2)
    max_dd = round((portfoy - portfoy.cummax()).min() * 100, 2)

    html = f"""
    <h1>📊 BIST AI PANEL</h1>
    <h2>Toplam Getiri: %{toplam_getiri}</h2>
    <h2>Sharpe: {sharpe}</h2>
    <h2>Max Drawdown: %{max_dd}</h2>
    <h3>Portföy:</h3>
    <ul>
        {''.join(f"<li>{h}</li>" for h in HISSELER)}
    </ul>
    """

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
