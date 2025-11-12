from .Data import Colors, TimeMode
import time
import os
from datetime import datetime

class Logger:
    def __init__(self, debug=False, time_mode=TimeMode.CHRONO, clear=True):
        self.default_color = Colors.DEFAULT
        self.buffer = ""
        self.debug_mode = debug
        self.time_mode = time_mode
        self.start = None
        if clear:
            self.clear_stdout()

    def clear_stdout(self):
        """ Clearing stdout """
        os.system('cls' if os.name == 'nt' else 'clear')

    def print(self, msg, color=Colors.DEFAULT):
        """ Print into stdout """
        print(color.value + msg + self.default_color.value)

    def print_rainbow(self, msg):
        """ Print with rainbow colors """
        color_loop = [
            Colors.PURPLE,
            Colors.BLUE,
            Colors.GREEN,
            Colors.YELLOW,
            Colors.ORANGE,
            Colors.DARK_ORANGE,
            Colors.RED,
            Colors.PINK
        ]
        for index in range(len(msg)):
            color = color_loop[index % len(color_loop)]
            print(color.value + msg[index], end='')
            
        print(self.default_color.value)
    
    def init(self):
        """ Initialize logger """
        self.cadre("BEGINNING OF LOGS", padding=2, color=Colors.BLUE)
        if self.time_mode == TimeMode.CHRONO:
            self.start_timer()

        mode = self.time_mode
        self.time_mode = TimeMode.DATE
        self.log("Debut des logs\n", dark=True)
        self.time_mode = mode
    
    def end(self, path="./file.log"):
        """ End of logs """
        elapsed = self.stop_timer()
        temps = ""
        hours = int(elapsed // 3600)
        if hours > 0:
            temps += f"{hours:02}h "

        minutes = int((elapsed % 3600) // 60)
        if minutes > 0 or temps != "":
            temps += f"{minutes:02}min "

        seconds = int(elapsed % 60)
        if seconds > 0 or temps != "":
            temps += f"{seconds:02}s "

        milliseconds = int((elapsed * 1000) % 1000)
        temps += f"{milliseconds:03}ms"
        self.section("END OF LOGS", char="=", color=Colors.BLUE)
        self.print(f"\nExecution time: {temps}\n", color=Colors.BLUE)
        self.save(path)


    def start_timer(self):
        """ Start log timer """
        self.start = time.time()

    def stop_timer(self):
        """ Stop log timer """
        res = time.time() - self.start
        self.start = None
        return res

    def get_time_date(self):
        """ Returns the time or the date """
        if self.time_mode == TimeMode.DATE:
            timestamp = time.time()
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%d/%m/%Y, %H:%M:%S")
        elif self.time_mode == TimeMode.TIME:
            timestamp = time.time()
            dt = datetime.fromtimestamp(timestamp)
            ms = dt.microsecond // 1000
            return dt.strftime("%H:%M:%S") + f".{ms:03}"
        else:
            if self.start is None:
                return "............"
            elapsed = time.time() - self.start
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed * 1000) % 1000)
            return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


    def log(self, msg, print=True, dark=False):
        """ Register a log, and print it (default) """
        str = f"[LOG]\t {self.get_time_date()}\t- " + msg
        self.buffer += str + "\n"

        if print:
            color = Colors.BLACK if dark else self.default_color
            self.print(str, color=color)

    def warn(self, msg, print=True):
        """ Register a warning log [PURPLE] """
        str = f"[WARN]\t {self.get_time_date()}\t- " + msg
        self.buffer += str + "\n"
        
        if print:
            self.print(str, color=Colors.PURPLE)
    
    def error(self, msg, print=True):
        """ Register an error log [RED] """
        str = f"[ERROR]\t {self.get_time_date()}\t- " + msg
        self.buffer += str + "\n"
        
        if print:
            self.print(str, color=Colors.RED)
    
    def success(self, msg, print=True):
        """ Register a success log [GREEN] """
        str = f"[SUCCES] {self.get_time_date()}\t- " + msg
        self.buffer += str + "\n"
        
        if print:
            self.print(str, color=Colors.GREEN)
    
    def fail(self, msg, print=True):
        """ Register a fail log [RED] """
        str = f"[FAILED] {self.get_time_date()}\t- " + msg
        self.buffer += str + "\n"
        
        if print:
            self.print(str, color=Colors.RED)

    def debug(self, msg):
        """ Print a debug output. Can be disabled setting self.debug = False """
        str = f"[DEBUG]\t {self.get_time_date()}\t- " + msg
        self.buffer += str + "\n"
        
        if self.debug_mode:
            self.print(str, color=Colors.YELLOW)

    def section(self, name, length=80, char=".", padding=2, color=Colors.DEFAULT):
        """ Create a separator to differenciate sections in log """
        remaining = length - len(name)
        half = remaining // 2
        print(
            color.value
            + "\n" * padding
            + char * (half - 1)
            + f" {name} "
            + char * (remaining - half - 1)
            + "\n" * (padding - 1)
            + self.default_color.value
        )
    
    def cadre(self, name, length=80, padding=1, color=Colors.DEFAULT):
        """ Print a rectangle avec le nom au milieu """
        remaining = length - len(name)
        half = remaining // 2
        char = "#"
        print(color.value)
        print(char * length)
        print((char + " " * (length - 2) + char + "\n") * padding, end="")
        print(
            "#" + " " * (half - 2)
            + f" {name} "
            + " " * (remaining - half - 2) + "#" + "\n",
            end=""
        )
        print((char + " " * (length - 2) + char + "\n") * padding, end="")
        print(char * length)
        print(self.default_color.value)
    
    def save(self, path="./file.log"):
        """ Save logs into logfile """
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.buffer)
            self.success(f"Logs saved to {path}")
        except Exception as e:
            self.fail(f"Could not save logs: {e}")

