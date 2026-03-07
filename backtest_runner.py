from engine.backtest_engine import run_backtest

symbols = [
    "ASELS.IS",
    "TUPRS.IS",
    "THYAO.IS",
    "EREGL.IS",
    "SISE.IS"
]

for s in symbols:

    run_backtest(s)

    print("----------------------")
