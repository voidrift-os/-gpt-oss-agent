def cap_position(balance_usd: float, price: float, max_pct: float) -> float:
    """Max units based on a balance% cap."""
    max_usd = balance_usd * max_pct
    return max(0.0, max_usd / price)


def position_from_risk(balance_usd: float, price: float, stop_distance: float, risk_pct: float) -> float:
    """
    Classic position sizing: size = (balance * risk_pct) / stop_distance, then convert to units.
    If no stop, caller can pass a heuristic stop distance or skip this method.
    """
    if stop_distance <= 0:
        return 0.0
    risk_usd = balance_usd * risk_pct
    units = risk_usd / stop_distance
    return max(0.0, units)
