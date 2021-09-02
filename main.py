import signal
import os
import sys

from threading             import Thread, Event
from datetime              import datetime, timedelta
from sys                   import platform

# PYSIDE 2
from PySide2               import QtCore
from PySide2.QtGui         import QColor
from PySide2.QtWidgets     import *

# GUI FILE
from ui_splash_screen      import Ui_SplashScreen
from ui_main               import Ui_MainWindow

# MINE
from binance_client        import Binance_Client
from twilio_communications import Twilio_Communications
from rake                  import Rake
from log                   import Log
from config_parser         import ConfigParser
from enums                 import *


### GLOBALS ###
g_thread_dict       = dict()
g_thread_exit_event = Event()
g_log_file          = Log()
g_cfg_file          = ConfigParser(g_log_file)
g_cfg_dict          = g_cfg_file.parse_config_file()

g_labelCreditsUnrealizedPnL = None
g_shortlongbalance          = None
g_openPositions             = None
g_gui_loaded = False

g_counter = 0
g_jumper  = 10



class MainWindow(QMainWindow):
    
    def __init__(self):

        global g_thread_exit_event
        global g_labelCreditsUnrealizedPnL
        global g_shortlongbalance
        global g_openPositions   
                
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.labelPercentageAccountTotal  = self.ui.labelPercentageCPU
        self.labelPercentageMarginRatio   = self.ui.labelPercentageGPU
        self.labelPercentageAvailableUSDT = self.ui.labelPercentageRAM
        self.labelCreditsUnrealizedPnL    = self.ui.labelCredits
        
     
        self.ui.btn_minimize.clicked.connect(self.showMinimized)
        self.ui.btn_maximize.clicked.connect(self.showMaximized)
        self.ui.btn_close.clicked.connect(self.quit_app)
        
        g_labelCreditsUnrealizedPnL = self.ui.labelCredits
        g_shortlongbalance          = self.ui.labelCredits_2
        g_openPositions             = self.ui.labelCredits_3

        # circular progress
        self.circularProgressAccountTotal  = self.ui.circularProgressCPU
        self.circularProgressMarginRatio   = self.ui.circularProgressGPU
        self.circularProgressAvailableUSDT = self.ui.circularProgressRAM
    
        ## ==> REMOVE STANDARD TITLE BAR
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)    # Remove title bar
        # need someway to move the app on the screen after removing title bar

    # ## ==> SET VALUES TO DEF progressBarValue
    def setValue(self, myvalue, labelPercentage, progressBarName, color, percentage=False):
        htmlText = """<p align="center"><span style=" font-size:40pt;">${VALUE}</span><span style=" font-size:30pt; vertical-align:super;"></span></p>"""
        if percentage:
            htmlText = """<p align="center"><span style=" font-size:40pt;">{VALUE}</span><span style=" font-size:30pt; vertical-align:super;">%</span></p>"""
        
        labelPercentage.setText(htmlText.replace("{VALUE}", str(myvalue)))

        # CALL DEF progressBarValue
        self.progressBarValue(float(myvalue), progressBarName, color)


    def progressBarValue(self, value, widget, color):

        # PROGRESSBAR STYLESHEET BASE
        styleSheet = """
        QFrame{
        	border-radius: 110px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} {COLOR});
        }
        """

        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000
        progress = (100.0 - value) / 100.0

        if progress < 0.0:
            progress = 0.001

        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        # FIX MAX VALUE
        if value == 100:
            stop_1 = "1.000"
            stop_2 = "1.000"

        # SET VALUES TO NEW STYLESHEET
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2).replace("{COLOR}", color)

        # APPLY STYLESHEET WITH NEW VALUES
        widget.setStyleSheet(newStylesheet)


    @QtCore.Slot()
    def quit_app(self):
        app.quit()


class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)


        ## ==> SET INITIAL PROGRESS BAR TO (0) ZERO
        self.progressBarValue(0)

        ## ==> REMOVE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)    # Remove title bar
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground) # Set background to transparent

        ## ==> APPLY DROP SHADOW EFFECT
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.ui.circularBg.setGraphicsEffect(self.shadow)

        ## QTIMER ==> START
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        
        # TIMER IN MILLISECONDS
        self.timer.start(15)

        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##


    ## DEF TO LOANDING
    ########################################################################
    def progress (self):
        global g_counter
        global g_jumper
        value = g_counter

        # HTML TEXT PERCENTAGE
        htmlText = """<p><span style=" font-size:68pt;">{VALUE}</span><span style=" font-size:58pt; vertical-align:super;">%</span></p>"""

        # REPLACE VALUE
        newHtml = htmlText.replace("{VALUE}", str(g_jumper))

        if (value > g_jumper):
            # APPLY NEW PERCENTAGE TEXT
            self.ui.labelPercentage.setText(newHtml)
            g_jumper += 10

        # SET VALUE TO PROGRESS BAR
        # fix max value error if > than 100
        if value >= 100: value = 1.000
        self.progressBarValue(value)

        # CLOSE SPLASH SCREE AND OPEN APP
        if g_counter > 100:

            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.main = MainWindow()
            self.main.show()

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        g_counter += 0.5

    ## DEF PROGRESS BAR VALUE
    ########################################################################
    def progressBarValue(self, value):

        # PROGRESSBAR STYLESHEET BASE
        styleSheet = """
        QFrame{
        	border-radius: 150px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} rgba(85, 170, 255, 255));
        }
        """

        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000
        progress = (100 - value) / 100.0

        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        # SET VALUES TO NEW STYLESHEET
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)

        # APPLY STYLESHEET WITH NEW VALUES
        self.ui.circularProgress.setStyleSheet(newStylesheet)



def set_gui_text(val, window: SplashScreen, label: QLabel, circle: QFrame, color: str, percentsign=False):
    """Assigns large text values in the GUI"""
    htmlText = """<p align="center"><span style=" font-size:40pt;">{VALUE}</span><span style=" font-size:30pt; vertical-align:super;"></span></p>"""
    label.setText(htmlText.replace("{VALUE}", str(val)))
    window.main.setValue(
        myvalue         = val,
        labelPercentage = label,
        progressBarName = circle,
        color           = color,
        percentage      = percentsign)


def set_gui_sub_text(label_name1, val1, label: QLabel, precise=False, money=False, label_name2=None, val2=None):
    """Assigns small text values in the GUI"""

    val_int = float(val1)

    if label_name2 is not None and val2 is not None:
        htmlText = f"<html><head/><body><p>short: <span style=\"color:#ffffff;\">{str(round(val1))} </span>long: <span style=\"color:#ffffff;\">{str(round(val2))}</span> </p></body></html>"
    else:
        if money and precise:
            val1 = '${:,.2f}'.format(float(val_int))
        elif money:
            val1 = f"${round(val_int)}"

        htmlText = f"<html><head/><body><p>{label_name1}: <span style=\" color:#ffffff;\">{val1}</span></p></body></html>"
    
    label.setText(htmlText.replace("{VALUE}", str(htmlText)))


def wait(timeout=1):
    """Causes thread to wait for 1 second and also
     checks if exit condition has been triggered"""
    global g_thread_exit_event
    if g_thread_exit_event.wait(timeout):
        print_log("Exiting main_loop thread", end=True)
        return True
    return False


def wait_till_gui_loads(window:SplashScreen):
    """Causes thread to wait until window.main is assigned a value"""
    global g_gui_loaded
    while True:
        try:
            if window.main:
                g_gui_loaded = True
                break
        except:
            wait(1)


def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


def signal_handler(signum, frame): # kill_app
    """https://blog.miguelgrinberg.com/post/how-to-kill-a-python-thread"""
    global g_thread_exit_event
    global g_log_file
    print(           f"[-] {get_current_time()} signal_handler exiting")
    g_log_file.write(f"[-] {get_current_time()} signal handler exiting")
    signal.signal(signum, signal.SIG_IGN) # ignore additional signals
    g_thread_exit_event.set()


def windows_sync_time():
    """Sync windows time in case we get disconnected from Binance API"""
    global g_log_file

    if platform == "linux" or platform == "linux2":
        # linux
        pass
    elif platform == "darwin":
        # OS X
        pass
    elif platform == "win32":
        # Windows...
        try:
            # https://docs.microsoft.com/en-us/troubleshoot/windows-server/identity/error-message-run-w32tm-resync-no-time-data-available
            # https://bwit.blog/tutorial-sync-server-time-ntp/
            print_log("w32tm /resync")
            if os.system("w32tm /resync") != 0:
                print_log("windows time sync failed")
                print_log("configuring windows time sync")
                os.system("w32tm /config /manualpeerlist:time.nist.gov /syncfromflags:manual /reliable:yes /update")
                os.system("Net stop w32time")
                os.system("Net start w32time")
            else:
                print_log("windows time sync successful")
        except Exception as e:
            print_log("failed to sync windows time", e=e)
            

def print_and_log(futures_wallet_value, current_margin_ratio, available_usdt, short_total, long_total):
    global g_log_file
    print(f"[+] {get_current_time()}", end=' ')
    print(f"futures_wallet_value: {'${:,.2f}'.format(futures_wallet_value)},", end=' ')
    print(f"current_margin_ratio: {'{:,.2f}'.format(current_margin_ratio)}%,", end=' ')
    print(f"available_usdt: {'${:,.2f}'.format(available_usdt)},", end=' ')
    print(f"short_total: {'${:,.2f}'.format(short_total)}, long_total: {'${:,.2f}'.format(long_total)}")
    g_log_file.write(f"[+] {get_current_time()} futures_wallet_value: {'${:,.2f}'.format(futures_wallet_value)}, current_margin_ratio: {'{:,.2f}'.format(current_margin_ratio)}%, available_usdt: {'${:,.2f}'.format(available_usdt)}, short_total: {'${:,.2f}'.format(short_total)}, long_total: {'${:,.2f}'.format(long_total)}")


def print_log(message, money=False, e=False, end=False):
    global g_log_file
    if money:
        print(           f"[$] {get_current_time()} {message}")
        g_log_file.write(f"[$] {get_current_time()} {message}")
        return
    if e:
        print(           f"[!] {get_current_time()} ERROR: {message}")
        print(           f"[!] {get_current_time()} {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}")
        g_log_file.write(f"[!] {get_current_time()} ERROR: {message}")
        g_log_file.write(f"[!] {get_current_time()} {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}")
        return
    if end:
        print(           f"[-] {get_current_time()} {message}")
        g_log_file.write(f"[-] {get_current_time()} {message}")
        return

    print(           f"[*] {get_current_time()} {message}")
    g_log_file.write(f"[*] {get_current_time()} {message}")


def init_threads():
    global g_thread_dict
    g_thread_dict["main_loop"] = Thread(target=main_loop, args=(window,))

    if RAKE:
        rake = Rake(parameter_dict=g_cfg_dict, exit_event=g_thread_exit_event, log_file=g_log_file)
        g_thread_dict["rake_every_trade"] = Thread(target=rake.rake_every_trade)

    for thread in g_thread_dict.values():
        thread.start()



#######################################################################################
### MAIN-LOOP ###
#######################################################################################
def main_loop(window: SplashScreen):
    global g_thread_dict
    global g_thread_exit_event
    global g_log_file
    global g_cfg_dict
    global g_shortlongbalance
    global g_labelCreditsUnrealizedPnL
    global g_openPositions
    global g_gui_loaded

    print_log("Starting main loop thread")

    disconnected_count = 0
    bnb_count          = 0
    future = timedelta(minutes=20) + datetime.now()

    binance_client = Binance_Client(g_cfg_dict, g_thread_exit_event, g_log_file)
    phone          = Twilio_Communications(g_cfg_dict, g_log_file)
    binance_client.limit_order_future = datetime.now()


    while True:

        if datetime.now() >= future:
            """Reset our binance client every RESET_TIME minutes to prevent disconnect error"""
            binance_client.client = Binance_Client(g_cfg_dict, g_thread_exit_event, g_log_file).client
            future = timedelta(minutes=BINANCE_CLIENT_RESET_TIME) + datetime.now()
            print_log(message=f"Reset binance_client. Next reset in {future.strftime('%H:%M:%S')}")
        
        if disconnected_count >= 20:
            """If we have tried to connect using the binance client 20 times or more, then we have disconnected"""
            message = "Anti-Liquidation Bot cannot connect to Binance. Check your internet connection."
            phone.send_disconnected_text(f"[*] {get_current_time()} {message}")
            print_log(message)
            disconnected_count = 0

        if wait(1): break

        current_margin_ratio_float          = binance_client.futures_get_account_margin_ratio()
        current_margin_ratio_str            = '{:,.2f}'.format(float(current_margin_ratio_float))
        short_total, long_total, hedge_mode = binance_client.auto_decide_hedge_mode()
        available_usdt                      = binance_client.futures_get_available_tether()
        futures_wallet_value                = round(binance_client.futures_get_wallet_value())

        if current_margin_ratio_float == -1 or short_total == -1 or long_total == -1 or hedge_mode == -1 or available_usdt == -1 or futures_wallet_value == -1:
            """Try syncing the time and resetting the variables to fix any issue"""
            print_log("Reseting variables and syncing windows time")
            windows_sync_time()
            binance_client.client = Binance_Client(g_cfg_dict, g_thread_exit_event, g_log_file).client
            phone                 = Twilio_Communications(g_cfg_dict, g_log_file)
            disconnected_count   += 1
            continue

        total_unrealizedPnL   = binance_client.futures_get_total_unrealized_profit()
        numopenPostitions     = len(binance_client.futures_get_all_open_positions())

        futures_account_value = binance_client.futures_get_wallet_value()
        one_day_profit        = binance_client.futures_get_todays_profit()
        yesterdays_value      = futures_account_value - one_day_profit

        if yesterdays_value == 0:
            yesterdays_value = 1
        
        todays_percentage     = (one_day_profit / yesterdays_value) * 100
        todays_percentage     = '{:,.2f}%'.format(todays_percentage)
        one_day_profit        = f"24 Hour USDT Profit: {'${:,.2f}'.format(one_day_profit)}"

        if not g_gui_loaded: 
            wait_till_gui_loads(window)

        set_gui_text(val=futures_wallet_value,     window=window, label=window.main.ui.labelPercentageCPU, circle=window.main.ui.circularProgressCPU, color="rgba(85, 170, 255, 255)")
        set_gui_text(val=current_margin_ratio_str, window=window, label=window.main.ui.labelPercentageGPU, circle=window.main.ui.circularProgressGPU, color="rgba(85, 255, 127, 255)", percentsign=True)
        set_gui_text(val=available_usdt,           window=window, label=window.main.ui.labelPercentageRAM, circle=window.main.ui.circularProgressRAM, color="rgba(255, 0, 127, 255)")
        
        set_gui_sub_text(label_name1="Unrealized PnL", label_name2=None,   val1=total_unrealizedPnL, val2=None,       label=g_labelCreditsUnrealizedPnL, precise=True,  money=True)
        set_gui_sub_text(label_name1="open positions", label_name2=None,   val1=numopenPostitions,   val2=None,       label=g_openPositions,             precise=False, money=False)
        set_gui_sub_text(label_name1="short",          label_name2="long", val1=short_total,         val2=long_total, label=g_shortlongbalance,          precise=False, money=True)

        window.main.ui.label_13.setText(get_current_time() + " " + one_day_profit + ", " + todays_percentage)

        if wait(1): break

        print_and_log(futures_wallet_value, current_margin_ratio_float, available_usdt, short_total, long_total)
        disconnected_count = 0
        bnb_count         += 1
        
        if wait(1): break

        #####################################################################
        ### ANTI-LIQUIDATION PROCEDURE ###
        if current_margin_ratio_float >= MARGIN_RATIO_THRESHOLD:
            phone.send_text(margin_ratio=current_margin_ratio_float)

            if wait(1): break

            phone.send_phone_call()
            binance_client.anti_liquidation_procedure()
        else:
            """Margin ratio dropped below MARGIN_RATIO_THRESHOLD, reset variables.
                Whew, we are no longer in danger of getting liquidated"""
            phone.has_sent_warning1_text       = False
            phone.has_sent_phone_call          = False
            binance_client.al_procedure_active = False
            
            open_positions = binance_client.futures_get_all_open_positions()

            if len(open_positions) == 1:
                if HEDGE_SYMBOL in open_positions:
                    binance_client.close_hedge()
                    binance_client.futures_cancel_order(HEDGE_SYMBOL)
            elif len(open_positions) == 0:
                open_orders = binance_client.futures_get_all_open_orders()
                for dictionary in open_orders:
                    if dictionary['symbol'] == HEDGE_SYMBOL:
                        binance_client.futures_cancel_order(HEDGE_SYMBOL)
                        break
        #####################################################################
        
        if wait(1): break

        # bnb_count is used to delay the resupply check.
        # We only need to resupply bnb every once in a while
        if bnb_count >= 100:
            binance_client.bnb_resupply()
            bnb_count = 0





#######################################################################################
### MAIN ###
#######################################################################################
if __name__ == "__main__":
    g_log_file.directory_create()
    g_log_file.file_create()
    
    # signal only works in main thread of the main interpreter
    signal.signal(signal.SIGINT, signal_handler)

    app    = QApplication(sys.argv)
    window = SplashScreen()

    print_log(message="Sync windows time on startup")
    windows_sync_time() # sync windows time on startup
    init_threads()      # start the threads
    app.exec_()         # start GUI
    
    # Woah, shut it down!
    signal_handler(signal.SIGINT, signal.SIG_IGN)
    print_log(message="Exiting main thread", end=True)
