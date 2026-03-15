from tradingview_ta import TA_Handler, Interval

def get_tv_analysis(symbol):

    try:

        handler = TA_Handler(
            symbol=symbol,
            screener="turkey",
            exchange="BIST",
            interval=Interval.INTERVAL_1_DAY
        )

        analysis = handler.get_analysis()

        return analysis.summary

    except:

        return None
