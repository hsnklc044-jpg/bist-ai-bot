import pandas as pd
import yfinance as yf


def check_portfolio():

    try:

        df = pd.read_csv(
            "data/portfolio.csv"
        )

        for index, row in df.iterrows():

            symbol = row["symbol"]

            data = yf.download(
                symbol,
                period="5d",
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if data.empty:
                continue

            if isinstance(data.columns, pd.MultiIndex):
                current_price = float(
                    data["Close"].iloc[:, 0].iloc[-1]
                )
            else:
                current_price = float(
                    data["Close"].iloc[-1]
                )

            if current_price >= row["target2"]:
                df.loc[index, "status"] = "TARGET2 HIT"

            elif current_price >= row["target1"]:
                df.loc[index, "status"] = "TARGET1 HIT"

            elif current_price <= row["stop"]:
                df.loc[index, "status"] = "STOP HIT"

            else:
                df.loc[index, "status"] = "OPEN"

        df.to_csv(
            "data/portfolio.csv",
            index=False
        )

        return True

    except Exception as e:

        print(
            f"[PORTFOLIO ERROR] {e}"
        )

        return False