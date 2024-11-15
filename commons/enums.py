from enum import Enum

class Action:
    BUY = "BUY"
    SELL = "SELL"

class ContractType:
    CE = "CE"
    PE = "PE"

class IndexType:
    BANKNIFTY = "BANKNIFTY"
    NIFTY = "NIFTY"


class TargetSlType:
    INDEXPOINT = "INDEXPOINT"
    INDEXPERCENT = "INDEXPERCENT"
    INSTRUMENTPOINT = "INSTRUMENTPOINT"
    INSTRUMENTPERCENT = "INSTRUMENTPERCENT"

class Month(Enum):
    """
    No longer in use.
    """
    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OCT = 10
    NOV = 11
    DEC = 12

class CoreFileName(Enum):
    YEAR_2016 = "_GFDLNFO_"
    YEAR_2017 = "_GFDLNFO_"
    YEAR_2018 = "_GFDLNFO_BACKADJUSTED_"
    YEAR_2019 = "_GFDLNFO_BACKADJUSTED_"
    YEAR_2020 = "_GFDLNFO_BACKADJUSTED_"
    YEAR_2021 = "_"
    YEAR_2022 = "_"
    YEAR_2023 = "_JF_FNO_"
    