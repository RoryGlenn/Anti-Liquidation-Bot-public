import os
import datetime
import time
import psutil
import glob

from threading import Thread


ALBOT   = "Anti-Liquidation-Bot"
LORDERS = "limit_orders.txt"
OORDERS = "open_orders.txt"
RTRADES = "raked_trades.txt"


def start_bot():
    print("starting bot")
    os.system(f"{ALBOT}.exe")


def stop_bot():
    print("stopping bot")
    os.system(f"TASKKILL /IM {ALBOT}.exe /T /F")


def is_bot_running():
    """return true if the AL bot is running"""
    for p in psutil.process_iter():
        if ALBOT in p.name():
            return True
    return False


def get_running_bot_name():
    """returns running bot name"""
    bot_name = None
    for p in psutil.process_iter():
        if ALBOT in p.name():
            bot_name = p
    return bot_name


def get_log_file_time():
    log_file_list = []
    
    """Has the log file been written too in the past 5 minutes?"""
    directory_path = os.getcwd() + "\\logs\\*"
    
    """get all the files in a folder and organize them by name and date"""
    file_list = glob.glob(directory_path)
    
    for file in file_list:
        names = file.split("\\")
        log_file_name = names[-1]
        if log_file_name == LORDERS or log_file_name == OORDERS or log_file_name == RTRADES:
            break
        else:
            log_file_list.append(file)
    
    """So if we are starting the bot up for the first time and there are no log files,
        wait a little longer until one is generated. 
        Log files on slower computers will take more time to be created"""
    if len(log_file_list) == 0:
        return None

    with open(log_file_list[-1], 'r') as file:
        """if the log file has not been written to in the past 5 minutes"""
        lines = file.readlines()
        last_line = lines[-1]
        
        last_line = last_line.split()
        time0 = str(log_file_list[-1]).split("\\")[-1].replace(".txt", "")
        time1 = last_line[1]
        times = time0 + " " + time1

        time_dt = datetime.datetime.strptime(times, '%Y-%m-%d %H:%M:%S')
        return time_dt


def has_time_passed():
    """compares more recent logfile time with current datetime"""
    logfile_dt = get_log_file_time()

    if logfile_dt is None:
        return False

    if datetime.datetime.now() > logfile_dt + datetime.timedelta(minutes=1):
        """if more than 5 minutes have passed, return true"""
        return True
    return False


def restart_bot():
    """if the bot is running and more than 5 minutes have passed
        since the log file was written to, restart the bot"""
    while True:
        if is_bot_running() and has_time_passed():
            stop_bot()
            Thread(target=start_bot).start()
        time.sleep(60)



if __name__ == "__main__":

    """if bot is not running, start the bot"""
    if not is_bot_running():
        Thread(target=start_bot).start()
        time.sleep(10)

    restart_bot()