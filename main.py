from commons.modules import pandas as pd, timedelta, logging, datetime, os
from commons.models import UserConfig
from config_loader import load_config
from expiry_builder import get_dataset_path_df
from strike_builder import strike_finder
from strike_builder import contract_maker
from expiry_builder import get_thursday_based_weekly_expiry
from commons.enums import TargetSlType
from commons.enums import Action
from commons.utils  import save_pnl_dict_to_csv

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

        
def take_trade(
    config: UserConfig, df_mapping: dict,pnl_dict: dict, leg_combination: list = ["CE", "PE"],
):
    contract_ce_df = df_mapping["contract_ce_df"]
    contract_pe_df = df_mapping["contract_pe_df"]

    for leg_type in leg_combination:
        if leg_type == "CE":
            df = contract_ce_df
            entry_price = df["Close"].iloc[0]
        else:
            df = contract_pe_df
            entry_price = df["Close"].iloc[0]

        date = df["Date"].iloc[0]
        symbol = df["Symbol"].iloc[0]
        
        target = config.target
        stoploss = config.stoploss
        trade_action = config.action
        entry_time = df["Time"].iloc[0]

        if config.target_sl_type == TargetSlType.INSTRUMENTPOINT:
            target_price, stoploss_price = (
                (entry_price + target, entry_price - stoploss)
                if config.action== Action.BUY
                else (entry_price - target, entry_price + stoploss)
            )

        elif config.target_sl_type == TargetSlType.INSTRUMENTPERCENT:
            target_price, stoploss_price = (
                (entry_price + ((entry_price*target)/100), entry_price - ((entry_price*stoploss)/100))
                if config.action == Action.BUY
                else (entry_price - ((entry_price*target)/100), entry_price + ((entry_price*stoploss)/100))
            )

        tgt_df = df[df["High"]>=target_price] if config.action == Action.BUY else df[df["Low"]<=target_price]
        sl_df = df[df["Low"]<=stoploss_price] if config.action == Action.BUY else df[df["High"]>=stoploss_price]

        min_exit_time = config.exit_time
        reason = 'Normal Exit'
        exit_price = df["Close"].iloc[len(df)-1]
        exit_time = df["Time"].iloc[len(df)-1]


        if not tgt_df.empty:
            if tgt_df["Time"].iloc[0] < min_exit_time:
                reason = "Taget hit"
                min_exit_time = tgt_df["Time"].iloc[0]
                exit_price = tgt_df["Close"].iloc[0]
                exit_time = tgt_df["Time"].iloc[0]
        if not sl_df.empty:
            if sl_df["Time"].iloc[0] < min_exit_time:
                reason = "Stoploss hit"
                min_exit_time = sl_df["Time"].iloc[0]
                exit_price = sl_df["Close"].iloc[0]
                exit_time = sl_df["Time"].iloc[0]
        if exit_price:
            pnl = exit_price - entry_price if trade_action == "BUY" else entry_price-exit_price
        
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

def main():
    
    config = load_config()
    
    # Generate the df which includes path, for a particular trading days.
    path_df = get_dataset_path_df(config)
    
    # Create the pnl_dict to store the multiple day's record.
    pnl_dict = {"Date": [], "Symbol": [], "EntryPrice": [], "Exitprice": [], "TradeAction":[], "PnL": [], "EntryTime": [], "ExitTime": [], "Reason": []}
    
    for i in range(len(path_df)):
        if path_df["PathExists"].iloc[i]:

            df_mapping = {}

            day_df = pd.read_feather(path_df["Path"].iloc[i])

            # Make particular index's dataframe
            index_df = day_df[
                (day_df["Symbol"] == f"{config.backtesting_symbol}-I")
                & (day_df["Time"] >= config.entry_time)
                & (day_df["Time"] <= config.exit_time)
            ]

            # Make Atm strikeprice based on nearest spot-price.
            strike_price = strike_finder(
                index_df["Close"].iloc[0], config.backtesting_symbol
            )
            # Make nearest possible expiry.
            expiry_date = get_thursday_based_weekly_expiry(index_df["Date"].iloc[1])
            # Generate the contract from the symbol,expiry, and strike
            contract_symbol = contract_maker(
                config.backtesting_symbol, expiry_date, strike_price
            )

            # based on the contract's symbol make the dataframe for the ce/pe both.  
            contract_ce_df = day_df[
                (day_df["Symbol"] == contract_symbol + "CE")
                & (day_df["Time"] >= config.entry_time)
                & (day_df["Time"] <= config.exit_time)
            ]
            contract_pe_df = day_df[
                (day_df["Symbol"] == contract_symbol + "PE")
                & (day_df["Time"] >= config.entry_time)
                & (day_df["Time"] <= config.exit_time)
            ]

            # TODO: check length logic needs to be applied here.
            df_mapping["index_df"] = index_df
            df_mapping["contract_ce_df"] = contract_ce_df
            df_mapping["contract_pe_df"] = contract_pe_df


            take_trade(config, df_mapping, pnl_dict)
    save_pnl_dict_to_csv(config,pnl_dict)

    




if __name__ == "__main__":
    main()
