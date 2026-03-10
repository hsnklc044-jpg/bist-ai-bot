from backtest_engine import run_backtest


def learn():

    result = run_backtest()

    if "Win Rate" not in result:
        return "Öğrenme verisi bulunamadı."

    try:

        lines = result.split("\n")

        for l in lines:
            if "Win Rate" in l:
                winrate = float(l.split("%")[1])

        if winrate > 60:
            status = "AI radar iyi çalışıyor."
        elif winrate > 50:
            status = "AI radar orta performans."
        else:
            status = "AI radar filtreleri geliştirilmeli."

        msg = f"""
🤖 AI Learning Report

{result}

Status: {status}
"""

        return msg

    except:

        return "AI öğrenme analizi yapılamadı."