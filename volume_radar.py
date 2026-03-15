from bist_data import get_price


def find_volume_spikes(symbols):

    results = []

    for s in symbols:

        try:

            df = get_price(s)

            avg_volume = df["Volume"].rolling(20).mean().iloc[-1]

            last_volume = df["Volume"].iloc[-1]

            if last_volume > avg_volume * 2:

                results.append(s)

        except:
            pass

    return results[:5]
