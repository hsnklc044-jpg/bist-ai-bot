import requests


def get_bist_symbols():

    url = "https://raw.githubusercontent.com/matfax/sp500/master/bist100.txt"

    try:

        r = requests.get(url)

        symbols = r.text.splitlines()

        return symbols

    except:

        return [
            "AKBNK","ASELS","BIMAS","EKGYO","EREGL","FROTO","GARAN",
            "HEKTS","ISCTR","KCHOL","KRDMD","ODAS","PETKM","SAHOL",
            "SASA","SISE","TAVHL","TCELL","THYAO","TOASO","TUPRS","YKBNK"
        ]


BIST_SYMBOLS = get_bist_symbols()