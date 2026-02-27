def efficient_frontier(mu, cov, num_portfolios=5000):

    results = []
    weights_record = []

    num_assets = len(mu)

    for _ in range(num_portfolios):

        weights = np.random.random(num_assets)
        weights /= np.sum(weights)

        port_return = np.sum(mu * weights)
        port_vol = np.sqrt(weights.T @ cov @ weights)
        sharpe = (port_return - RISK_FREE_RATE) / port_vol

        results.append([port_return, port_vol, sharpe])
        weights_record.append(weights)

    results = np.array(results)

    max_sharpe_idx = np.argmax(results[:,2])
    min_vol_idx = np.argmin(results[:,1])

    return {
        "max_sharpe": {
            "return": results[max_sharpe_idx,0],
            "vol": results[max_sharpe_idx,1],
            "sharpe": results[max_sharpe_idx,2],
            "weights": weights_record[max_sharpe_idx]
        },
        "min_vol": {
            "return": results[min_vol_idx,0],
            "vol": results[min_vol_idx,1],
            "sharpe": results[min_vol_idx,2],
            "weights": weights_record[min_vol_idx]
        }
    }
