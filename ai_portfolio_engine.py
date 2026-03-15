from ai_score_engine import ai_scan


def build_portfolio():

    try:

        results = ai_scan()

        if not results:
            return []

        # Skora göre sırala (yüksekten düşüğe)
        results = sorted(results, key=lambda x: x[1], reverse=True)

        portfolio = []

        for stock, score in results:

            portfolio.append((stock, score))

            if len(portfolio) == 5:
                break

        return portfolio

    except Exception as e:

        print("AI Portfolio Engine hata:", e)

        return []