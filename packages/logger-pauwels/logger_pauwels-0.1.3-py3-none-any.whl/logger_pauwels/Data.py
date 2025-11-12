from enum import Enum

class Colors(Enum):
    DEFAULT = "\033[0m"
    BLACK = "\033[30m"
    DARK_GRAY = "\033[90m"
    GRAY = "\033[37m"
    LIGHT_GRAY = "\033[37;1m"
    WHITE = "\033[97m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    PINK = "\033[95m"
    PURPLE = "\033[35m"
    YELLOW = "\033[33m"
    ORANGE = "\033[38;5;208m"
    DARK_ORANGE = "\033[38;5;202m"
    CYAN = "\033[36m"

class TimeMode(Enum):
    CHRONO = "Chrono"
    DATE = "Date"
    TIME = "Time"