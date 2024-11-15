from commons.modules import datetime, logging, pandas as pd, os
from commons.models import UserConfig

from commons.enums import TargetSlType
from commons.enums import Action

logger = logging.getLogger(__name__)


# Create the pnl_dict to store the multiple day's record.
pnl_dict = {
    "Date": [],
    "Symbol": [],
    "EntryPrice": [],
    "Exitprice": [],
    "TradeAction": [],
    "PnL": [],
    "EntryTime": [],
    "ExitTime": [],
    "EntryTimeIndex": [],
    "ExitTimeIndex": [],
    "Reason": [],
}


def save_pnl_dict_to_csv(
    config: UserConfig,
    pnl_dict: dict,
    file_name: str = None,
    path: str = None,
    folder_name: str = "results",
):
    """
    Converts `pnl_dict` to a `pnl_df` and stores it as a CSV file at a specified location.

    The function creates a folder structure with the format `results/DD-MM-YYYY/` by default at root directory,
    where `DD-MM-YYYY` is the current date. The file is saved as `{backtesting_symbol}_{hour}_{minute}_{second}.csv`.
        eg: results\14-11-2024\BANKNIFTY_12_31_26.csv

    or

    we can decide path at where we want to store the result
    by providing
        path = "D:\ArkalogiTanmay\Backtesting\commons" or
        file_name = "test01.csv" or
        folder_name = "result2k24"
    """
    try:
        logger.info("Starting storing pnl df")
        pnl_df = pd.DataFrame(pnl_dict)
        current_time = datetime.datetime.now()
        current_date = current_time.strftime("%d-%m-%Y")
        folder_path = (
            os.path.join(path, folder_name, current_date)
            if path
            else os.path.join(folder_name, current_date)
        )

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if not file_name:
            file_name = f"{config.backtesting_symbol}_{current_time.hour}_{current_time.minute}_{current_time.second}.csv"

        file_path = os.path.join(folder_path, file_name)

        pnl_df.to_csv(file_path, index=False)
        logger.info("Completed storing pnl df")

    except Exception as ex:
        logger.info(f"Error at result strorinng, reason is: {ex}")
        raise ex


def take_trade(
    config: UserConfig,
    df_mapping: dict,
    pnl_dict: dict,
    leg_combination: list = ["CE", "PE"],
):
    index_df = df_mapping["index_df"]
    contract_ce_df = df_mapping["contract_ce_df"]
    contract_pe_df = df_mapping["contract_pe_df"]

    for leg_type in leg_combination:
        if leg_type == "CE":
            df = contract_ce_df
            entry_price = df["Close"].iloc[0]
            entry_time_index = index_df["Close"].iloc[0]
        else:
            df = contract_pe_df
            entry_price = df["Close"].iloc[0]
            entry_time_index = index_df["Close"].iloc[0]

        date = df["Date"].iloc[0]
        symbol = df["Symbol"].iloc[0]

        target = config.target
        stoploss = config.stoploss
        trade_action = config.action
        entry_time = df["Time"].iloc[0]

        if config.target_sl_type == TargetSlType.INSTRUMENTPOINT:
            target_price, stoploss_price = (
                (entry_price + target, entry_price - stoploss)
                if config.action == Action.BUY
                else (entry_price - target, entry_price + stoploss)
            )

        elif config.target_sl_type == TargetSlType.INSTRUMENTPERCENT:
            target_price, stoploss_price = (
                (
                    entry_price + ((entry_price * target) / 100),
                    entry_price - ((entry_price * stoploss) / 100),
                )
                if config.action == Action.BUY
                else (
                    entry_price - ((entry_price * target) / 100),
                    entry_price + ((entry_price * stoploss) / 100),
                )
            )

        tgt_df = (
            df[df["High"] >= target_price]
            if config.action == Action.BUY
            else df[df["Low"] <= target_price]
        )
        sl_df = (
            df[df["Low"] <= stoploss_price]
            if config.action == Action.BUY
            else df[df["High"] >= stoploss_price]
        )

        min_exit_time = config.exit_time
        reason = "Normal Exit"
        exit_price = df["Close"].iloc[len(df) - 1]
        exit_time = df["Time"].iloc[len(df) - 1]
        exit_time_index = index_df["Close"].iloc[0]

        if not tgt_df.empty:
            if tgt_df["Time"].iloc[0] < min_exit_time:
                reason = "Taget hit"
                min_exit_time = tgt_df["Time"].iloc[0]
                exit_price = tgt_df["Close"].iloc[0]
                exit_time = tgt_df["Time"].iloc[0]
                exit_time_index = index_df["Close"].iloc[0]
        if not sl_df.empty:
            if sl_df["Time"].iloc[0] < min_exit_time:
                reason = "Stoploss hit"
                min_exit_time = sl_df["Time"].iloc[0]
                exit_price = sl_df["Close"].iloc[0]
                exit_time = sl_df["Time"].iloc[0]
                exit_time_index = index_df["Close"].iloc[0]
        if exit_price:
            pnl = (
                exit_price - entry_price
                if trade_action == "BUY"
                else entry_price - exit_price
            )

        # print()
        # print("*"*50)
        # print("Date", date)
        # print("symbol: ",symbol)
        # print("EntryPrice: ",entry_price)
        # print("Exitprice: ",exit_price)
        # print("TradeAction: ",trade_action)
        # print("PnL: ",pnl)
        # print("EntryTime: ",entry_time)
        # print("ExitTime: ",exit_time)
        # print("reason: ",reason)
        # print("*"*50)
        # print()
        pnl_dict["Date"].append(date)
        pnl_dict["Symbol"].append(symbol)
        pnl_dict["EntryPrice"].append(entry_price)
        pnl_dict["Exitprice"].append(exit_price)
        pnl_dict["TradeAction"].append(trade_action)
        pnl_dict["PnL"].append(pnl)
        pnl_dict["EntryTime"].append(entry_time)
        pnl_dict["ExitTime"].append(exit_time)
        pnl_dict["Reason"].append(reason)
        pnl_dict["EntryTimeIndex"].append(entry_time_index)
        pnl_dict["ExitTimeIndex"].append(exit_time_index)
