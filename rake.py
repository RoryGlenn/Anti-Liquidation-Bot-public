import datetime
import os

from enums          import *
from binance        import Client
from log            import Log
from binance_client import Binance_Client



class Rake(Binance_Client):
    
    def __init__(self, parameter_dict, exit_event, log_file: Log):
            self.binance_client          = Client(api_key    = parameter_dict['binance_api_key'], 
                                                  api_secret = parameter_dict['binance_secret_key'],
                                                  tld        = 'com')
                                                  
            self.log_file                = log_file
            self.thread_exit_event       = exit_event
            self.account_trades_list     = list()
            self.total_raked             = 0.0


    def get_current_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")


    def get_current_date(self):
        return datetime.date.today()


    def print_log(self, message, money=False):
        if not money:
            print(              f"[*] {self.get_current_time()} {message}")
            self.log_file.write(f"[*] {self.get_current_time()} {message}")
        else:
            print(              f"[$] {self.get_current_time()} {message}")
            self.log_file.write(f"[$] {self.get_current_time()} {message}") 

    def timeout_log(self, t):
        self.windows_sync_time()


    def exception_log(self, e, message):
        print(              f"[!] {self.get_current_time()} ERROR: {e}, {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}")
        print(              f"[!] {self.get_current_time()} ERROR: {message}")
        self.log_file.write(f"[!] {self.get_current_time()} ERROR: {message}")   
        self.log_file.write(f"[!] {self.get_current_time()} ERROR: {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}")        


    def handle_exception(self, e, message):
        self.exception_log(e, message)
        if str(e.code) == ERROR_TIME: # resync windows time
            self.timeout_log(e)


    def update_trade_list(self):
        """Gets all trades from 1 hour ago til now"""
        self.account_trades_list = self.futures_get_trades()


    def file_create(self):
        try:
            if not os.path.exists(RAKED_TRADES_FILE):
                file = open(RAKED_TRADES_FILE, "w+") # create the file
                file.close()
            
            # If its out first time opening the file since we started up,
            # write a new line to make it a little neater
            with open(RAKED_TRADES_FILE, 'a') as file:
                file.write("\n=========================================================================================\n")
        except Exception as e:
            self.handle_exception(e, f"can't create {RAKED_TRADES_FILE}")
            


    def write(self, text):
        """Writes to the end of the log file"""
        try:
            with open(RAKED_TRADES_FILE, 'a') as file:
                file.write(f"{self.get_current_date()} {self.get_current_time()} {text}\n")
        except Exception as e:
            self.handle_exception(e, f"can't write to {RAKED_TRADES_FILE}")


    def get_futures_realized_pnl(self):
        """Gets realized PnL (profit) made for the last hour in usdt"""
        try:
            realizedPnl         = 0.0
            account_trades      = self.binance_client.futures_account_trades()
            account_trades_list = list(account_trades)
            one_hour_ago        = datetime.datetime.now() - datetime.timedelta(hours=1)
            
            account_trades_list.reverse()

            for trade in account_trades_list:
                time_of_trade    = datetime.datetime.fromtimestamp(int(trade['time']) / 1000)
                if time_of_trade < one_hour_ago:
                    break
                realizedPnl += float(trade['realizedPnl'])
        except Exception as e:
            self.handle_exception(e, f"can't get futures realized pnl")
        return round(realizedPnl, 2)


###################################################################################################
### TRANSFER ###
###################################################################################################
    def futures_to_spot_transfer(self, realizedPnl, symbol="USDT"):
        """
        1: transfer from spot account to USDT-Ⓜ futures account.
        2: transfer from USDT-Ⓜ futures account to spot account.
        """

        # if there is no USDT available
        usdt_available = self.futures_get_available_tether()
        if usdt_available <= NOTHING:
            self.print_log(f"Can't transfer {realizedPnl} {symbol} from futures to spot. No available {symbol}.")
            return
        
        try:
            self.binance_client.futures_account_transfer(
                asset            = symbol,
                amount           = realizedPnl,
                type             = 2,
                dualSidePosition = False,
                recvWindow       = RECV_WINDOW)

            self.print_log(f"Raked {'${:,.4}'.format(realizedPnl)}", money=True)
        except Exception as e:
            self.handle_exception(e, f"Could not move {symbol} {realizedPnl} from futures to spot wallet")


    def spot_to_flex(self, productId, amount):
        try:
            if amount < FLEXIBLE_SAVINGS_USDT_MIN:
                self.print_log(f"Can't move {productId} {amount} from spot to flexible savings. Must meet minimum of ${FLEXIBLE_SAVINGS_USDT_MIN}")
                return

            self.binance_client.purchase_lending_product(productId=productId+"001", amount=amount, recvWindow=RECV_WINDOW) 
            self.print_log(f"Moved to flexible savings: {productId} {'${:,.4f}'.format(amount)}")
        except Exception as e:
            self.handle_exception(e, f"Could not move to flexible savings {productId} {'${:,.4f}'.format(amount)}")



###################################################################################################
### SPOT ###
###################################################################################################

    def spot_get_usdt(self):
        try:
            account = self.binance_client.get_account()
            quantity_usdt = 0
            balances = account['balances']
            for dictionary in balances:
                if dictionary['asset'] == 'USDT':
                    quantity_usdt = float(dictionary['free'])
                    break
        except Exception as e:
            self.handle_exception(e, "Could not get spot usdt")            
        return round(quantity_usdt, 2)


    def spot_convert_usdt_to_busd(self):
        quantity_usdt = self.spot_get_usdt()

        # $10 is the min to buy BUSD/USDT
        if quantity_usdt >= BUSDUSDT_MIN:
            try:
                self.binance_client.order_market_buy(
                    symbol     = BUSDUSDT,
                    type       = MARKET,
                    quantity   = quantity_usdt,
                    recvWindow = RECV_WINDOW)
            except Exception as e:
                self.handle_exception(e, "Could not convert usdt to busd")
        else:
            self.print_log(f"Need at least 10 USDT in SPOT account in order to buy BUSD/USDT")




###################################################################################################
### FUTURES ###
###################################################################################################

    def futures_get_trades(self):
        """Gets all trades made for the last 24 hours"""
        trade_list = list()
        try:
            account_trades      = self.binance_client.futures_account_trades(limit=100, recvWindow=RECV_WINDOW)
            account_trades_list = list(account_trades)
            account_trades_list.reverse()
            for dictionary in account_trades_list:
                if float(dictionary['realizedPnl']) > 0.0: 
                    trade_list.append(dictionary)
        except Exception as e:
            self.handle_exception(e, "Could not get futures trades")
        return trade_list


###################################################################################################
### RAKE ###
###################################################################################################

    def rake_every_trade(self):
        """Once rake_every_trade() has been started, we do"""
        realizedPnL = 0.0
        self.file_create()
        self.update_trade_list()
        self.print_log("Starting rake thread")
        
        # Make sure to document the trades that have a negative PnL 
        
        while True:
            while True:
                if self.thread_exit_event.wait(timeout=RAKE_THREAD_WAIT_TIME):
                    print(              f"[-] {self.get_current_time()} exiting rake thread")
                    self.log_file.write(f"[-] {self.get_current_time()} exiting rake thread")
                    return

                trade_list = self.futures_get_trades()

                for dictionary in trade_list:
                    if dictionary not in self.account_trades_list:
                        realizedPnL += float(dictionary['realizedPnl'])
                        self.print_log(f"New trade found: {dictionary}", money=True)
                        self.write(    f"[$] New trade found: {dictionary}")

                if realizedPnL > 0.0:
                    """update our list and prepare to rake profit"""
                    self.print_log(message=f"Realized profit: {'${:,.4f}'.format(realizedPnL)}", money=True)
                    self.account_trades_list = trade_list.copy()
                    break


            amount_to_rake = realizedPnL * RAKE_PERCENT
            
            realizedPnL = 0.0 # DON'T MOVE THIS ABOVE amount_to_rake! 

            if amount_to_rake < USDT_TRANSFER_MIN:
                self.print_log(f"{'${:,.4f}'.format(amount_to_rake)} is too low to rake")
                continue

            # get the amount of USDT in our spot account
            spot_usdt = self.get_spot_coin_balance(USDT)

            self.futures_to_spot_transfer(amount_to_rake, symbol=USDT)
            
            # if the amount_to_rake in our spot account meets the minimum to stake, then stake self.total_raked
            if amount_to_rake + spot_usdt >= FLEXIBLE_SAVINGS_USDT_MIN:
                self.spot_to_flex("USDT", amount_to_rake+spot_usdt)





###################################################################################################
### LENDING ACCOUNT ###
###################################################################################################

    def lending_account_get_value(self):
        totalAmountInUSDT = 0.0
        try:
            totalAmountInUSDT = self.binance_client.get_lending_account()['totalAmountInUSDT']
            totalAmountInUSDT = float(totalAmountInUSDT)
        except Exception as e:
            self.handle_exception(e, "could not get lending account value")
        return totalAmountInUSDT






###################################################################################################
### STAKING ACCOUNT ###
###################################################################################################

    def staking_account_move_to(self, productId, amount):
        try:
            customized = self.binance_client.get_fixed_activity_project_list(type="CUSTOMIZED_FIXED", size=100, recvWindow=RECV_WINDOW)
            for d in customized:
                print(d)
        except Exception as e:
            self.handle_exception(e, "could not move to staking account")