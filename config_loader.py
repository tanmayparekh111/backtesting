from commons.modules import datetime, json, os, logging
from commons.models import UserConfig
from commons.contsants import DATASET_FOLDER
from commons.enums import (
    TargetSlType,
    Action,
    IndexType,
)

logger = logging.getLogger(__name__)


def load_config(config_file: str = "config.json") -> UserConfig:
    '''
    Take all the parameter from the  user in config.json,
    then load it to the `UserCongif`
    '''
    # Set the speco00foc error msg
    err_msg = None
    try:
        logger.info("**Started confifg loading***")
        with open(config_file, "r") as f:
            config = json.load(f)

        entry_time = datetime.datetime.strptime(config["entry_time"], "%H:%M").time()
        exit_time = datetime.datetime.strptime(config["exit_time"], "%H:%M").time()

        from_date = datetime.datetime.strptime(config["from_date"], "%Y-%m-%d").date()
        to_date = datetime.datetime.strptime(config["to_date"], "%Y-%m-%d").date()

        if from_date>to_date:
            err_msg = "Kindly check your from_date: {from_date} which shouldn't greater than the ro_date: {to_date}"
            raise Exception

        backtesting_symbol = (
            IndexType.BANKNIFTY
            if config["backtesting_symbol"] == "BANKNIFTY"
            else IndexType.NIFTY if config["backtesting_symbol"] == "NIFTY" else None
        )
        action = (
            Action.BUY
            if config["action"] == "BUY"
            else Action.SELL if config["action"] == "SELL" else None
        )

        target = float(config["target"])
        stoploss = float(config["stoploss"])

        target_sl_type = (
            TargetSlType.INDEXPOINT
            if config["target_sl_type"] == "INDEXPOINT"
            else (
                TargetSlType.INDEXPERCENT
                if config["target_sl_type"] == "INDEXPERCENT"
                else (
                    TargetSlType.INSTRUMENTPOINT
                    if config["target_sl_type"] == "INSTRUMENTPOINT"
                    else (
                        TargetSlType.INSTRUMENTPERCENT
                        if config["target_sl_type"] == "INSTRUMENTPERCENT"
                        else None
                    )
                )
            )
        )
        if (not target_sl_type) or (not action) or (not backtesting_symbol):
            err_msg = "Kindly check your parameters in config for target_sl_type, action, or backtesting_symbol"
            raise Exception

        dataset_folder = DATASET_FOLDER

        if dataset_folder:
            current_dir = os.getcwd()
            files_at_dataset = os.listdir(current_dir + dataset_folder)
            files_at_dataset.remove("Holidays")
        else:
            err_msg = "Kindly, set the `DATASET_FOLER` inside the commons.constant"
            raise Exception

        # Load all the parameters to the Userconfig
        config = UserConfig(
            entry_time=entry_time,
            exit_time=exit_time,
            from_date=from_date,
            to_date=to_date,
            backtesting_symbol=backtesting_symbol,
            action=action,
            target=target,
            stoploss=stoploss,
            dataset_folder=dataset_folder,
            target_sl_type=target_sl_type,
            current_dir=current_dir,
            files_at_dataset=files_at_dataset,
        )
        logger.info("**Successfully loaded confifg***")

    except Exception as ex:
        if err_msg:
            logger.info(f"Error at config loading, reason is: {err_msg}")
        else:
            logger.info(f"Error at config loading, reason is: {ex}")
        raise ex

    return config
