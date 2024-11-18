from commons.modules import (
    pandas as pd,
    os,
    timedelta,
    logging,
)

from commons.models import UserConfig
from commons.enums import CoreFileName

logger = logging.getLogger(__name__)


def check_holiday(expiry_date):
    """
    This function is used to check the given date is the holiday or not.
    """
    try:
        current_dir = os.getcwd()
        holiday_path = f"{current_dir}\data_bnf_nf\Holidays\{expiry_date.year}.feather"
        holiday_df = pd.read_feather(holiday_path)
        holidays = holiday_df["Date"].unique()

        if str(expiry_date) in holidays:
            return 1

    except Exception as ex:
        logger.info(f"Error at check_holiday, reason is: {ex}")
        raise ex

    return 0

def get_next_thursday(trading_date):
    """
    This function is used to find the nearest thursday on any given `trading_day`.
    """

    # Find which day it is, e.g mon-0, tues-1, wed-2, thurs-3, .., sun-6.
    trading_weekday = trading_date.weekday()

    # Find how many days needed to add to get to the Thursday.
    # for mon-thursday(0-3 ==> expiry will be same thursday
    if trading_weekday <= 3:
        days_until_thursday = 3 - trading_weekday
    else:
        # for fri-sunday(4-6)  ==> expiry will be next thursday
        days_until_thursday = (7 - trading_weekday) + 3

    next_thursday = trading_date + timedelta(days=days_until_thursday)

    return next_thursday


def get_thursday_based_weekly_expiry(trading_date) -> str:
    """
    This function is used to find the nearest thursday on any given `trading_day`,
    but it also filter it based on the next `next_thursday` if it is holidaty it will -1 it.
    """
    try:
        expiry_date = None

        expiry_date = get_next_thursday(trading_date)
        while check_holiday(expiry_date):
            expiry_date = expiry_date - timedelta(days=1)
            # TODO: Here if trading day > expiry
            # in that case it should take a next expiry.

        formatted_expiry_date = expiry_date.strftime("%d%b%y").upper()

    except Exception as ex:
        logger.info(f"issue in finding weekly expiry, and the reson is{ex}")

    return formatted_expiry_date

def get_dataset_path_df(config: UserConfig):

    """
    Takes the `UserConfig` as the input,
    and make the valid trading day's path datafame and return it.
    """

    try:
        logger.info("Started finding dataset path for the backtesting")
        from_date = config.from_date
        to_date = config.to_date

        current_date = from_date
        path_dict = {"Date": [], "PathExists": [], "Path": [], "HolidayReason": []}

        while current_date <= to_date:

            path_dict["Date"].append(current_date)

            # Check wheather this day is sat,  sun, or theb Holiday.
            if (
                (current_date.weekday() == 5)
                or (current_date.weekday() == 6)
                or check_holiday(current_date)
            ):
                path_exists = False
                path = None
                holiday_reason = "Weekend / National Holiday"

            # If today is not the holiday, then make the possible path for the day.
            else:
                formatted_date = current_date.strftime("%d%m%Y")
                backtesting_year = str(current_date.strftime("%Y"))
                core_name = CoreFileName[f"YEAR_{backtesting_year}"].value
                
                # Make a path upto the symbol named folder in our dataset.
                folder_path = os.path.join(
                    (config.current_dir + config.dataset_folder),
                    backtesting_year,
                    current_date.strftime("%b").upper(),
                    config.backtesting_symbol,
                )

                # Make a file name
                file_name = (
                    f"{config.backtesting_symbol}{core_name}{formatted_date}.feather"
                )

                # Make file path  by joining (folder_path &  file_name)
                file_path = os.path.join(folder_path, file_name)

                if os.path.exists(os.path.join(file_path)):
                    path_exists = True
                    path = file_path
                    holiday_reason = None
                # for some days we do not have the data, for those days store info accordingly. 
                else:
                    path_exists = False
                    path = None
                    holiday_reason = "Data Not Available"

            # Move current_day on the next_day
            current_date += timedelta(days=1)

            # Store the info to the path_dict
            path_dict["PathExists"].append(path_exists)
            path_dict["Path"].append(path)
            path_dict["HolidayReason"].append(holiday_reason)

        path_df = pd.DataFrame(path_dict)
        logger.info("Completed finding dataset path for the backtesting")
    except Exception as ex:
        logger.info(f"Erro at dataset path making, reason is: {ex}")

    return path_df
