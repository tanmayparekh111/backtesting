from commons.modules import datetime
from commons.enums import Action, IndexType
from commons.contsants import DATASET_FOLDER


class UserConfig:
    def __init__(
        self,
        entry_time: datetime.time,
        exit_time: datetime.time,
        from_date: datetime.date,
        to_date: datetime.date,
        backtesting_symbol: IndexType,
        action: Action,
        target: float,
        stoploss: float,
        target_sl_type: str,
        current_dir: str,
        files_at_dataset: str,
        dataset_folder: str = DATASET_FOLDER,
    ):
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.from_date = from_date
        self.to_date = to_date
        self.backtesting_symbol = backtesting_symbol
        self.action = action
        self.target = target
        self.stoploss = stoploss
        self.target_sl_type = target_sl_type
        self.current_dir = current_dir
        self.files_at_dataset = files_at_dataset
        self.dataset_folder = dataset_folder


class Trade:
    def __init__(self): ...
