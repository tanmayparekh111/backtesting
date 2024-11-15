def strike_finder(spot_price: float, instrument: str = "BANKNIFTY") -> str:
    """
    Rounds the given spot price to the nearest strike price based on the instrument's rounding rules.
    - For "BANKNIFTY", rounds to the nearest 100; for "NIFTY", rounds to the nearest 50.
    """
    
    round_off_mapping = {"BANKNIFTY": 100, "NIFTY": 50}
    round_off_value = round_off_mapping[instrument]

    rounded_down = int(spot_price // round_off_value) * round_off_value
    diff = spot_price - round_off_value

    # TODO: Need to add this 50 as a dynamic. 
    if diff > 50:
        strike_price = rounded_down + round_off_value
    else:
        strike_price = rounded_down
    
    return str(strike_price)

def contract_maker(symbol: str, expiry_date: str, strike_price: str) -> str:
    return str(symbol + expiry_date + strike_price)