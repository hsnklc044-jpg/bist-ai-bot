from portfolio_system.pnl_engine import PNLEngine


engine = PNLEngine()

results = engine.calculate()

for trade in results:

    print("\n-------------------")

    print(
        f"Symbol: "
        f"{trade['symbol']}"
    )

    print(
        f"Signal: "
        f"{trade['signal']}"
    )

    print(
        f"Entry: "
        f"{trade['entry_price']}"
    )

    print(
        f"Current: "
        f"{trade['current_price']}"
    )

    print(
        f"PnL %: "
        f"{trade['pnl_percent']}"
    )