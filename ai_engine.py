import random

symbols = [
"EREGL",
"THYAO",
"ASELS",
"KRDMD",
"SASA",
"TUPRS",
"SISE",
"AKBNK",
"GARAN"
]

def get_support_levels(symbol):

```
price = random.uniform(50, 150)

return {
    "symbol": symbol,
    "s1": round(price * 0.97, 2),
    "s2": round(price * 0.94, 2),
    "s3": round(price * 0.90, 2),
    "r1": round(price * 1.03, 2),
    "r2": round(price * 1.06, 2),
    "r3": round(price * 1.10, 2)
}
```

def generate_signals():

```
signals = []

for s in symbols:

    score = random.randint(6, 10)

    if score >= 7:

        support = round(random.uniform(50, 100), 2)

        signals.append({
            "symbol": s,
            "score": score,
            "support": support,
            "target": round(support * 1.10, 2),
            "stop": round(support * 0.97, 2)
        })

return signals
```

def get_hot_stocks():

```
results = []

for s in symbols:

    volume = round(random.uniform(1.5, 4), 2)
    score = random.randint(7, 10)

    if volume > 2:

        results.append({
            "symbol": s,
            "score": score,
            "volume": volume
        })

return results
```
