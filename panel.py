@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    # GET gelirse test mesajı döndür
    if request.method == "GET":
        return "Webhook aktif", 200

    data = request.get_json(silent=True)

    if not data:
        return "No JSON", 200

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            handle_start(chat_id)
        else:
            send_telegram(chat_id, f"Komut alındı: {text}")

    return "ok", 200
