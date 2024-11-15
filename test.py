from commons.enums import Action
from commons.modules import logging
from commons.utils import get_current_dateime

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger  = logging.getLogger(__name__)




curr_datetime = get_current_dateime()
# logger.warning(f"value: {curr_datetime}")
# logger.info(Action.BUY)