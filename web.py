from flask import Flask
import threading
import scheduler

app = Flask(__name__)

@app.route("/")
def home():
    return "BIST AI BOT running"

def run_scheduler():
    scheduler.start()

thread = threading.Thread(target=run_scheduler)
thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
