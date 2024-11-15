from commons.modules import pandas as pd, timedelta, logging, datetime, os
from commons.models import UserConfig
from config_loader import load_config
from expiry_builder import get_dataset_path_df
from strike_builder import strike_finder
from strike_builder import contract_maker
from expiry_builder import get_thursday_based_weekly_expiry
from commons.utils import save_pnl_dict_to_csv
from commons.utils import take_trade
from commons.utils import pnl_dict

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():

    config = load_config()

    # Generate the df which includes path, for a particular trading days.
    path_df = get_dataset_path_df(config)

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

            # If not expiry, strike_price or contract_symbol is made just skip that day.
            if (not expiry_date) or (not strike_price) or (not contract_symbol):
                continue

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
    save_pnl_dict_to_csv(config, pnl_dict)


if __name__ == "__main__":
    main()
