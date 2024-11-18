from commons.modules import logging
from commons.enums import InstrumentStrikeGap

logger = logging.getLogger(__name__)

def strike_finder(spot_price: float, instrument: str = "BANKNIFTY") -> str:
    """
    Rounds the given spot price to the nearest strike price based on the instrument's rounding rules.
    - For "BANKNIFTY", rounds to the nearest 100; for "NIFTY", rounds to the nearest 50.
    """
    try:
        strike_price = None
        round_off_value = InstrumentStrikeGap.BANKNIFTY if instrument == "BANKNIFTY" else InstrumentStrikeGap.NIFTY if instrument == "NIFTY" else None
        strike_price = (spot_price // round_off_value) * round_off_value
        b = strike_price + round_off_value
        return int(b if spot_price - strike_price > b - spot_price else strike_price)
    except Exception as ex:
        logger.info(f"Issue in strike price making for a single day, the reason is {ex}")
    
    return str(strike_price)

def contract_maker(symbol: str, expiry_date: str, strike_price: str) -> str:
    return str(symbol + expiry_date + strike_price)