import json
from datetime import datetime


def save_trade(trade):

    try:

        try:
            with open("trade_journal.json","r") as f:
                data = json.load(f)
        except:
            data = []

        trade["date"] = datetime.now().strftime("%Y-%m-%d")

        data.append(trade)

        with open("trade_journal.json","w") as f:
            json.dump(data,f,indent=4)

    except:
        pass


def get_journal():

    try:

        with open("trade_journal.json","r") as f:
            return json.load(f)

    except:
        return []
