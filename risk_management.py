def position_sizing(account_size, risk_per_trade, entry_price, stop_loss_price):
    """
    Calculate position size based on account size, risk per trade, entry price, and stop-loss price.
    """
    risk_amount = account_size * risk_per_trade
    risk_per_share = entry_price - stop_loss_price
    position_size = risk_amount / risk_per_share
    return position_size

def kelly_criterion(win_rate, win_loss_ratio):
    """
    Calculate the optimal bet size using the Kelly criterion.
    """
    kelly_fraction = (win_rate - (1 - win_rate) / win_loss_ratio)
    return kelly_fraction

def drawdown_control(peaks_and_valleys):
    """
    Calculate the maximum drawdown based on peaks and valleys of account balance.
    """
    max_drawdown = 0
    peak = peaks_and_valleys[0]

    for valley in peaks_and_valleys:
        if valley > peak:
            peak = valley
        drawdown = (peak - valley) / peak
        max_drawdown = max(max_drawdown, drawdown)
    return max_drawdown

def risk_validation(current_risk, max_risk):
    """
    Validate if current risk is within acceptable limits.
    """
    if current_risk > max_risk:
        raise ValueError("Current risk exceeds maximum allowed risk.")
    return True