from flask import Flask
from ai_radar_engine import radar_scan
from bist100_engine import scan_bist100

app = Flask(__name__)


@app.route("/")
def home():

    radar_results = radar_scan()

    html = "<h1>BIST AI Dashboard</h1>"

    html += "<h2>AI Radar</h2>"

    if radar_results is None or len(radar_results) == 0:

        html += "<p>Radar sinyali yok</p>"

    else:

        for r in radar_results:

            html += f"<p>{r[0]} | Score: {r[1]}</p>"


    html += "<br><a href='/scanner'>BIST100 Scanner</a>"

    return html



@app.route("/scanner")
def scanner():

    results = scan_bist100()

    html = "<h1>BIST100 Scanner</h1>"

    if results is None or len(results) == 0:

        html += "<p>Sinyal bulunamadı</p>"

    else:

        for r in results:

            html += f"<p>{r[0]} | Score: {r[1]}</p>"

    html += "<br><a href='/'>Ana Sayfa</a>"

    return html



if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
