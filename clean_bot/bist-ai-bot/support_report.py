from core.support_resistance import get_support_resistance

symbol = "EREGL.IS"

data = get_support_resistance(symbol)

if data:

    report = f"""
📊 {data['symbol']} ANALYSIS

Price : {data['price']}

🟢 SUPPORTS

S1 : {data['support1']}
S2 : {data['support2']}

🔴 RESISTANCES

R1 : {data['resistance1']}
R2 : {data['resistance2']}
"""

    print(report)