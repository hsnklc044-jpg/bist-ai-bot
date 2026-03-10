def filter_elite_signals(results):

    elite = []

    for r in results:

        if r["score"] >= 65 and r["rr"] >= 1.8:

            elite.append(r)

    elite = sorted(elite, key=lambda x: x["score"], reverse=True)

    return elite[:3]
