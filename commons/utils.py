from commons.modules import (
    datetime,
    logging,
    pandas as pd,
    os
)
from commons.models import UserConfig

logger = logging.getLogger(__name__)

def save_pnl_dict_to_csv(config:UserConfig, pnl_dict: dict,file_name: str = None, path: str = None, folder_name: str = 'results'):
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
        pnl_df = pd.DataFrame(pnl_dict)
        current_time = datetime.datetime.now()
        current_date = current_time.strftime("%d-%m-%Y")
        folder_path = os.path.join(path,folder_name,current_date) if path else os.path.join(folder_name,current_date)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        
        if not file_name:
            file_name = f"{config.backtesting_symbol}_{current_time.hour}_{current_time.minute}_{current_time.second}.csv"
        
        file_path = os.path.join(folder_path,file_name)

        pnl_df.to_csv(file_path, index=False)
        
    except Exception as ex:
        logger.info(f"==Error at result strorinng, reason is: {ex}")
        raise ex