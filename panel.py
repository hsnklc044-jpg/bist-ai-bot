from flask import Flask, request, render_template_string, redirect
import os

app = Flask(__name__)

# Render environment variable'dan şifreyi al
PANEL_PASSWORD = os.environ.get("PANEL_PASSWORD", "1234")

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>BIST AI Panel</title>
    <style>
        body {
            background:#0b1b33;
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
            font-family:Arial;
        }
        .box {
            background:#1f2e4a;
            padding:40px;
            border-radius:12px;
            text-align:center;
            color:white;
            width:300px;
        }
        input {
            padding:10px;
            width:90%;
            margin-top:10px;
            border-radius:6px;
            border:none;
        }
        button {
            margin-top:15px;
            padding:10px 20px;
            background:#22c55e;
            border:none;
            border-radius:8px;
            color:white;
            font-weight:bold;
            cursor:pointer;
        }
        .err {color:#ff4d4d; margin-top:10px;}
    </style>
</head>
<body>
    <div class="box">
        <h2>🔐 BIST AI Panel</h2>
        <form method="post">
            <input type="password" name="password" placeholder="Şifre giriniz">
            <br>
            <button type="submit">Giriş Yap</button>
        </form>
        {% if error %}
        <div class="err">❌ Hatalı şifre</div>
        {% endif %}
    </div>
</body>
</html>
"""

PANEL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Panel</title>
</head>
<body style="background:#0b1b33;color:white;text-align:center;padding-top:80px;">
    <h1>📊 BIST AI PANEL AKTİF</h1>
    <p>Bot başarıyla çalışıyor.</p>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == PANEL_PASSWORD:
            return redirect("/panel")
        return render_template_string(LOGIN_HTML, error=True)

    return render_template_string(LOGIN_HTML, error=False)


@app.route("/panel")
def panel():
    return render_template_string(PANEL_HTML)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
