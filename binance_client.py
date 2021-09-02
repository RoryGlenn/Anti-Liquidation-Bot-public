import datetime
import os
import time
import platform

from enums             import *
from binance           import Client
from order_type        import OrderType, PositionSideType, SideType
from threading         import Thread, Event
from log               import Log
from ast               import literal_eval
from binance.client    import BinanceAPIException


class Binance_Client():

    def __init__(self, parameter_dict: dict, exit_event: Event, log_file: Log):
        self.api_key        = parameter_dict['binance_api_key']
        self.api_secret     = parameter_dict['binance_secret_key']
        self.client = Client(self.api_key, self.api_secret, tld='com')

        self.open_orders     = list()
        self.al_limit_orders = list()

        self.current_day = self.get_current_date()

        self.hedge_entry_price = 0.0

        self.exit_event = exit_event
        self.log_file   = log_file

        self.limit_order_future = datetime.datetime.now()

        self.has_saved_open_orders        = False
        self.end_handle                   = False
        self.has_started_mr_threshold     = False
        self.has_started_reopen_threshold = False
        self.al_procedure_active          = False
        self.has_set_limit_orders         = False
        self.has_hedge_stop_loss          = False



    def exception_log(self, e, message):
        # self.log_file.check_date(self.current_day)
        print(              f"[!] {self.get_current_time()} ERROR: {e}, {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}")
        print(              f"[!] {self.get_current_time()} ERROR: {message}")
        self.log_file.write(f"[!] {self.get_current_time()} ERROR: {message}")
        self.log_file.write(f"[!] {self.get_current_time()} ERROR: {e}, {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}")        


    def handle_exception(self, e, message):
        self.exception_log(e, message)

        # if type(e).__name__ == "ConnectionError": # ('Connection aborted.', OSError("(10054, 'WSAECONNRESET')")), ConnectionError
        self.client = None
        if self.wait(30): 
            return
        self.client = Client(self.api_key, self.api_secret, tld='com')

        self.print_log("Reset binance client")

        if isinstance(e, BinanceAPIException):
            if str(e.code) == ERROR_TIME: # resync windows time
                self.windows_sync_time()

    
    def print_log(self, message, money=False):
        """Prints to console and writes data to log file"""
        if not money:
            print(              f"[*] {self.get_current_time()} {message}")
            self.log_file.write(f"[*] {self.get_current_time()} {message}")
        else:
            print(              f"[$] {self.get_current_time()} {message}")
            self.log_file.write(f"[$] {self.get_current_time()} {message}")            


    def get_current_date(self):
        """Gets current date"""
        return datetime.date.today()


    def get_current_time(self):
        """Gets current time in hour, minute, second format"""
        return datetime.datetime.now().strftime("%H:%M:%S")


    # https://stackoverflow.com/questions/43441883/how-can-i-make-a-file-hidden-on-windows
    def hide_file(self, filename):
        """Hides a file from the user"""
        os.system(f"attrib +h {filename}")


    # https://stackoverflow.com/questions/43441883/how-can-i-make-a-file-hidden-on-windows
    def unhide_file(self, filename):
        """Un-hides a file from the user"""
        os.system(f"attrib -h {filename}")


    def file_create(self):
        """Creates a .txt file"""
        try:
            if not os.path.exists(LIMIT_ORDERS_FILE):
                file = open(LIMIT_ORDERS_FILE, "w+") # create the file
                file.close()
                self.hide_file(LIMIT_ORDERS_FILE)
        except Exception as e:
            self.handle_exception(e, f"can't create {LIMIT_ORDERS_FILE}")
            


    def write(self, text):
        """Writes to the end of the file"""
        try:
            if os.path.exists(LIMIT_ORDERS_FILE):
                self.unhide_file(LIMIT_ORDERS_FILE)

            with open(LIMIT_ORDERS_FILE, 'a') as file:
                file.write(f"{text}\n")
            
            self.hide_file(LIMIT_ORDERS_FILE)
        except Exception as e:
            self.handle_exception(e, f"can't write to {LIMIT_ORDERS_FILE}")


    def read(self):
        """Read data from LIMIT_ORDERS_FILE"""
        data = []
        try:
            if os.path.exists(LIMIT_ORDERS_FILE):
                self.unhide_file(LIMIT_ORDERS_FILE)
                with open(LIMIT_ORDERS_FILE, 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        line = literal_eval(line.strip("\n")) # convert line to dictionary
                        data.append(line)
                self.hide_file(LIMIT_ORDERS_FILE)
        except Exception as e:
            self.handle_exception(e, f"can't write to {LIMIT_ORDERS_FILE}")
        return data


    def windows_sync_time(self):
        """Sync windows time in case we get disconnected from Binance API
        WARNING: This function only works if the user runs the .exe as administrator!"""

        if platform == "linux" or platform == "linux2": # linux
            pass
        elif platform == "darwin": # OS X
            pass
        elif platform == "win32": # Windows...
            try:
                # https://docs.microsoft.com/en-us/troubleshoot/windows-server/identity/error-message-run-w32tm-resync-no-time-data-available
                self.print_log("w32tm /resync")

                if os.system("w32tm /resync") != 0:
                    self.print_log("windows time sync failed")
                    os.system("w32tm /config /manualpeerlist:time.nist.gov /syncfromflags:manual /reliable:yes /update")
                    os.system("Net stop w32time")
                    os.system("Net start w32time")
                else:
                    self.print_log("windows time sync successful")
            except Exception as e:
                self.handle_exception(e, "failed to sync windows time")




    def futures_get_max_precision(self, symbol):
        precision = 0
        with open(FUTURES_MAX_PRECISION_FILE, 'r') as file:
            lines = file.readlines()
            for line in lines:
                symbol_ = line.split()
                if symbol_[0] == symbol:
                    decimal = float(symbol_[1])
                    if decimal == 1:
                        precision = 0
                    else:
                        precision = len(str(decimal)) - 2
                    break
        return precision 


    def futures_get_symbol_min_trade_quantity(self, symbol):
        min_trade = 0.001
        with open(FUTURES_MIN_TRADE_AMOUNTS, 'r') as file:
            lines = file.readlines()
            for line in lines:
                symbol_ = line.split()
                if symbol_[0] == symbol:
                    min_trade = float(symbol_[1])
                    break
        return min_trade               







###################################################################################################
### BNB RESUPPLY ###
###################################################################################################

    def bnb_resupply(self):
        """If BNB quantity in futures account is 0, buy 1% of futures account value.
           If 1% is below $11.00, buy $11 instead. Then transfer BNB back into futures wallet to get 10% trading fee discount"""

        if not BUY_BNB:
            return

        try:
            bnb_current_quantity = 1.0
            bnb_quantity_to_buy  = 0.0
            balance              = self.client.futures_account_balance()
            
            for dictionary in balance:
                if dictionary['asset'] == BNB:
                    bnb_current_quantity = float(dictionary['balance'])
                    break

            bnb_current_quantity = round(bnb_current_quantity, 2)

            if bnb_current_quantity == NOTHING:
                usdt_spot_quantity         = self.get_spot_coin_balance(symbol=USDT)
                available_usdt             = self.futures_get_available_tether()
                bnb_mark_price             = self.futures_get_mark_price("BNBUSDT")
                usdt_quantity_to_transfer  = available_usdt * 0.01


                if available_usdt < BNB_BUY_MIN:
                    self.print_log(f"Can't buy bnb. Need at least $10. Available usdt is ${available_usdt}")
                    return

                if bnb_mark_price == 0.0:
                    self.print_log(f"Can't buy bnb. Mark price of BNB is ${bnb_mark_price}")
                    return


                if usdt_quantity_to_transfer <= BNB_BUY_MIN:
                    usdt_quantity_to_transfer = BNB_BUY_MIN
                    self.print_log("USDT transfer too low, setting transfer amount to $11.00")

                if usdt_spot_quantity < BNB_BUY_MIN:
                    # transfer money to spot account
                    self.futures_to_spot_transfer(usdt_quantity_to_transfer)

                # check if the transfer from futures to spot was successful
                usdt_spot_quantity = self.get_spot_coin_balance(symbol=USDT)

                if usdt_spot_quantity < usdt_quantity_to_transfer:
                    self.print_log(f"Can't buy bnb. Spot transfer failed")
                    return

                bnb_quantity_to_buy = (usdt_quantity_to_transfer - 0.90) / bnb_mark_price
                bnb_quantity_to_buy = round(bnb_quantity_to_buy, 4)

                # min amount of BNB to buy is BNB_BUY_MIN
                notional = self.get_notional_value(bnb_mark_price, bnb_quantity_to_buy, BNB_MIN)

                if bnb_quantity_to_buy < notional:
                    bnb_quantity_to_buy = notional

                self.client.order_market(
                    symbol     = "BNBUSDT",
                    side       = SideType.SIDE_BUY,
                    quantity   = bnb_quantity_to_buy,
                    recvWindow = RECV_WINDOW)

                self.print_log(f"Bought BNB/USDT {bnb_quantity_to_buy}")

                # check the quantity of bnb we just bought
                bnb_spot_qty = self.get_spot_coin_balance(symbol=BNB)

                # transfer BNB back in futures
                self.spot_to_futures_transfer(asset=BNB, amount=bnb_spot_qty)
        except Exception as e:
            self.handle_exception(e, "Could not resupply bnb")

            


###################################################################################################
### LONG ###
###################################################################################################

    def futures_close_long_position(self, symbol, quantity):
        """Closes a long position in futures account"""
        if quantity <= NOTHING:
            self.print_log(f"can't close {symbol} long position because you own {quantity}")
            return

        try:
            self.client.futures_create_order(
                symbol     = symbol, 
                side       = SideType.SIDE_SELL, 
                type       = OrderType.FUTURE_ORDER_TYPE_MARKET, 
                quantity   = quantity,
                reduceOnly = True,
                recvWindow = RECV_WINDOW)

            self.print_log(f"closed {symbol} {quantity} long position")
        except Exception as e:
            self.handle_exception(e, "Could not close futures long position")            



    def futures_place_long_position(self, quantity, symbol=HEDGE_SYMBOL):
        """Creates a long position"""
        usdt_futures_quantity = float(self.futures_get_available_tether())
        quantity              = abs(round(quantity, 3))

        if quantity <= NOTHING:
            self.print_log(f"Can't place {symbol} long with {quantity} quantity")
            return

        if usdt_futures_quantity <= NOTHING:
            self.print_log(f"Not enough USDT available to place the {HEDGE_SYMBOL} {quantity} long hedge. Current USDT: {usdt_futures_quantity}")
            return

        try:
            self.client.futures_create_order(
                symbol       = symbol,
                side         = SideType.SIDE_BUY,
                positionSide = PositionSideType.BOTH, 
                type         = OrderType.FUTURE_ORDER_TYPE_MARKET,
                quantity     = quantity,
                recvWindow	 = RECV_WINDOW)
            
            self.print_log(f"Placed {symbol} {quantity} long hedge")
        except BinanceAPIException as b:
            if str(b.code) == ERROR_MARGIN_INSUFFICIENT:
                self.print_log(f"Insufficient margin: {symbol} {quantity}")
                return ERROR_MARGIN_INSUFFICIENT
        except Exception as e:
            self.handle_exception(e, f"Could not place {symbol} {quantity} long position")


    def futures_get_open_long_interest(self):
        """Gets the total amount of all long positions by adding them all together"""
        open_long_interest = 0.0
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if float(dictionary['positionAmt']) > NOTHING:  # for long positions
                    open_long_interest += (float(dictionary['positionAmt']) * float(dictionary['entryPrice'])) / float(dictionary['leverage'])
        except Exception as e:
            self.handle_exception(e, "Could not get open long interest")
        return open_long_interest


    def futures_get_open_long_interest_with_leverage(self):
        """Gets the total amount of all long positions by adding them all together"""
        open_long_interest = 0.0
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if float(dictionary['positionAmt']) > NOTHING:  # for long positions
                    open_long_interest += float(dictionary['positionAmt']) * float(dictionary['entryPrice'])
        except Exception as e:
            self.handle_exception(e, "Could not get open long interest with leverage")        
        return open_long_interest


###################################################################################################
### SHORT ###
###################################################################################################

    def futures_close_short_position(self, symbol, quantity):
        """Closes a short position in futures account"""
        try:
            self.client.futures_create_order(
                symbol     = symbol, 
                side       = SideType.SIDE_BUY, 
                type       = OrderType.FUTURE_ORDER_TYPE_MARKET, 
                quantity   = abs(float(quantity)),
                reduceOnly = True,
                recvWindow = RECV_WINDOW)

            self.print_log(f"closed {symbol} {quantity} short position")
        except Exception as e:
            self.handle_exception(e, f"Could not close {symbol} {quantity} short position")


    def futures_get_open_short_interest(self):
        """Gets the total amount of all short positions by adding them all together without leverage"""
        open_short_interest = 0.0
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if float(dictionary['positionAmt']) < NOTHING:  # for short positions
                    open_short_interest += (float(dictionary['positionAmt']) * float(dictionary['entryPrice']) ) / float(dictionary['leverage'])
        except Exception as e:
            self.handle_exception(e, "Could not open short interest")
        return open_short_interest


    def futures_get_open_short_interest_with_leverage(self):
        """Gets the total amount of all short positions by adding them all together with leverage factored in"""
        open_short_interest = 0.0
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if float(dictionary['positionAmt']) < NOTHING:
                    open_short_interest += float(dictionary['positionAmt']) * float(dictionary['entryPrice'])
        except Exception as e:
            self.handle_exception(e, "Could not open short interest with leverage")
        return open_short_interest


    def futures_place_short_position(self, quantity, symbol=HEDGE_SYMBOL):
        """Creates a short position"""
        usdt_futures_quantity = float(self.futures_get_available_tether())
        quantity              = abs(round(quantity, 3))

        if quantity <= NOTHING:
            self.print_log(f"Can't place {HEDGE_SYMBOL} short with {quantity} quantity")
            return

        if usdt_futures_quantity <= NOTHING:
            self.print_log(f"Not enough USDT available to place the {HEDGE_SYMBOL} {quantity} short hedge. Current USDT: {usdt_futures_quantity}")
            return

        try:
            self.client.futures_create_order(
                        symbol      = symbol,
                        side         = SideType.SIDE_SELL,
                        positionSide = PositionSideType.BOTH, 
                        type         = OrderType.FUTURE_ORDER_TYPE_MARKET,
                        quantity     = quantity,
                        recvWindow	 = RECV_WINDOW)
            
            self.futures_set_hedge_entry_price()

            self.print_log(f"Placed {HEDGE_SYMBOL} {quantity} Short hedge")
        except BinanceAPIException as b:
            if str(b.code) == ERROR_MARGIN_INSUFFICIENT:
                self.print_log(f"Insufficient margin: {symbol} {quantity}")
                return ERROR_MARGIN_INSUFFICIENT
        except Exception as e:
            self.handle_exception(e, f"could not place short position {HEDGE_SYMBOL} {quantity}")


###################################################################################################
### QUANTITY ###
###################################################################################################

    def futures_get_short_position_quantity(self, symbol):
        """Gets the quantity of a short position"""
        result = 0.0
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if dictionary['symbol'] == symbol:
                    if float(dictionary['positionAmt']) < NOTHING:  # for long positions
                        result = dictionary['positionAmt']
                        break
        except Exception as e:
            self.handle_exception(e, f"could not get short position {symbol}")
        return result


    def futures_get_long_position_quantity(self, symbol):
        """Gets the quantity of the long position"""
        result = 0.0
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if dictionary['symbol'] == symbol:
                    if float(dictionary['positionAmt']) > NOTHING:  # for long positions
                        result = dictionary['positionAmt']
                        break
        except Exception as e:
            self.handle_exception(e, "Could not get futures long position quantity")
        return result


    def futures_get_position_quantity(self, symbol):
        """Gets the quantity of the coin we own"""
        quantity = 0.0
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if dictionary['symbol'] == symbol:
                    quantity = dictionary['positionAmt']
                    break
        except Exception as e:
            self.handle_exception(e, "Could not get futures position quantity")
        return float(quantity)


###################################################################################################
### HEDGE ###
###################################################################################################

    def auto_decide_hedge_mode(self):
        """
        Decide which direction is better to hedge.
            This is done by adding up every long position and every short position in our futures account. 
            If our long_count is greater than our short_count, then we will hedge in the short direction.
            If our short_count is greater than our long_count, then we will hedge in the long direction.
            Upon error, return -1,-1,-1
        """
        short_count    = 0
        long_count     = 0
        hedge_decision = "Short"

        try:
            positions = self.client.futures_account(recvWindow=RECV_WINDOW)['positions']
            """ Adds up the amount of money we are using with leverage"""
            for dictionary in positions:
                if float(dictionary["positionAmt"]) < 0.0:
                    short_count += float(dictionary['positionAmt']) * float(dictionary['entryPrice'])
                elif float(dictionary["positionAmt"]) > 0.0:
                    long_count += float(dictionary['positionAmt']) * float(dictionary['entryPrice'])
            if abs(short_count) > long_count:
                hedge_decision = "Long"
            if abs(short_count) < long_count:
                hedge_decision = "Short"
        except Exception as e:
            self.handle_exception(e, "Could not decide hedge mode")
            return -1, -1, -1
        return round(short_count,3), round(long_count,3), hedge_decision


    def futures_set_hedge_leverage(self):
        """Set the leverage for our hedge position. This works for both short and long"""
        try:
            self.client.futures_change_leverage(
                symbol     = HEDGE_SYMBOL, 
                leverage   = HEDGE_LEVERAGE, 
                recvWindow = RECV_WINDOW)
        except Exception as e:
            self.handle_exception(e, "Could not set hedge leverage")


    def futures_get_current_hedge_entry_price(self):
        """Gets the average buy price (entry_price) for HEDGE_SYMBOL.
            Helpful Hint:
                The term "entry_price" on Binance is a little deceiving because when read literally,
                we think of the price the coin was originally bought at.
                While this is true if the coin was bought once and only once, 
                this is not true if the coin was bought 2 or more times at different prices.
                Once the coin is bought 2 or more times at different prices, the "entry_price" 
                becomes the break even price or average buy price."""
        current_entry_price = 0
        try:
            hedge_position = self.client.futures_position_information(symbol=HEDGE_SYMBOL, recvWindow=RECV_WINDOW)
            for dictionary in hedge_position:
                current_entry_price = float(dictionary['entryPrice'])
                break
        except Exception as e:
            self.handle_exception(e, "Could not set hedge leverage")        
        return current_entry_price


    def futures_set_hedge_entry_price(self):
        """Sets the entry price for our hedge position. 
        This function is used in conjunction with setting the hedge stop loss."""
        try:
            if self.hedge_entry_price == 0:
                hedge_position = self.client.futures_position_information(symbol=HEDGE_SYMBOL, recvWindow=RECV_WINDOW)
                for dictionary in hedge_position:
                    self.hedge_entry_price = float(dictionary['entryPrice'])
                    break
        except Exception as e:
            self.handle_exception(e, "Could not set hedge entry price")


    def create_hedge_stop_loss(self, side, stop_percent):
        """Puts a market stop loss in for our hedge position"""
        try:
            # if the hedge entry_price is the same as when the position was originally filled and there is already a hedge order open
            # get HEDGE_SYMBOL current entry price and compare with self.hedge_entry_price

            current_entry_price = self.futures_get_current_hedge_entry_price()

            if self.has_hedge_stop_loss: 
                if self.hedge_entry_price == current_entry_price: # when we first create the hedge, this condition will always be true
                    # self.print_log(f"Not placing new stop loss order for hedge {HEDGE_SYMBOL}. Hedge entry price ({self.hedge_entry_price}) = Current entry price ({current_entry_price})")
                    return

            self.has_hedge_stop_loss = True


            mark_price = self.futures_get_mark_price(HEDGE_SYMBOL)
            quantity   = self.futures_get_position_quantity(HEDGE_SYMBOL)
            stop_price = mark_price + (mark_price * stop_percent)

            quantity   = abs(round(quantity, 3))   # might need to get the min quantity from the .txt file
            stop_price = round(stop_price, 2)

            if quantity <= NOTHING:
                self.print_log(f"Can't place {HEDGE_SYMBOL} hedge stop loss with {quantity} quantity")
                return

            self.client.futures_create_order(
                symbol       = HEDGE_SYMBOL,
                side         = side,
                positionSide = PositionSideType.BOTH,
                type         = OrderType.FUTURE_ORDER_TYPE_STOP_MARKET,
                quantity     = abs(quantity),
                stopPrice    = stop_price,
                reduceOnly   = True,
                recvWindow	 = RECV_WINDOW)
            
            self.futures_set_hedge_entry_price()
            self.print_log(f"Placed {HEDGE_SYMBOL} {quantity} {'${:,.2f}'.format(float(stop_price))} stop")
        except Exception as e:
            self.handle_exception(e, f"could not place {HEDGE_SYMBOL} {stop_price} stop")



    def create_hedge(self):
        """
        create_hedge(): (This is the main component for creating a hedge).
            Based on the SHORT_LONG_RATIO_LIMIT_PERCENT that is set in config, gets the balance of shorts to longs to find out how much to hedge in either direction
            If we already have a HEDGE_SYMBOL position open in the opposite direction that we are trying to hedge, close it first then make the hedge.
            After the hedge is created, put a stop loss in for 10% lower than entry price for a long, 10 percent higher than entry price for a short.
        """

        usdt_available       = self.futures_get_available_tether()
        _, _, hedge_mode     = self.auto_decide_hedge_mode()
        long_interest        = round(self.futures_get_open_long_interest_with_leverage(), 1)
        short_interest       = round(abs(self.futures_get_open_short_interest_with_leverage()), 1)
        hedge_limit          = long_interest * HEDGE_PERCENT
        usdt_amount_to_hedge = hedge_limit - short_interest
        
        self.futures_change_margin_type(symbol=HEDGE_SYMBOL, margin_type=CROSS)
        self.futures_set_hedge_leverage()
        
        if self.end_handle:
            return

        if hedge_mode == "Short":
            if long_interest == 0:
                return

            balance = abs(short_interest / long_interest)

            if balance >= SHORT_LONG_RATIO_LIMIT_PERCENT and balance <= 100:
                """If the open interest on our hedge position is within SHORT_TO_LONG_BALANCE_RATIO of the hedge we want to make, don't make the new hedge"""
                self.print_log(f"short to long open interest balance is {'{:,.2f}'.format(balance*100)}%")
                return
            elif balance > 100:
                if self.futures_get_position_quantity(HEDGE_SYMBOL) != 0: # check if position exists
                    self.print_log("Rebalancing short interest")
                    short_interest = round(abs(self.futures_get_open_short_interest_with_leverage()), 1)                    
                    long_interest  = round(self.futures_get_open_long_interest_with_leverage(), 1)
                    interest_diff  = short_interest - long_interest
                    
                    # in order to rebalance, we need to close some of our HEDGE_SYMBOL position
                    mark_price = self.futures_get_mark_price(HEDGE_SYMBOL)   # calculate how much we need to short based on open long positions
                    quantity   = round((interest_diff/mark_price), 3)        # calculate quantity of coin to short
                    
                    self.futures_cancel_order(HEDGE_SYMBOL)
                    self.futures_close_short_position(HEDGE_SYMBOL, quantity)
                    self.create_hedge_stop_loss(side=SideType.SIDE_BUY, stop_percent=HEDGE_STOP_PERCENT)
                    return


            mark_price = self.futures_get_mark_price(HEDGE_SYMBOL)   # calculate how much we need to short based on open long positions
            quantity   = round((usdt_amount_to_hedge/mark_price), 3) # calculate quantity of coin to short

            self.futures_cancel_order(HEDGE_SYMBOL)

            result = ERROR_MARGIN_INSUFFICIENT
            if quantity != 0:
                result = self.futures_place_short_position(symbol=HEDGE_SYMBOL, quantity=quantity)

            if result == ERROR_MARGIN_INSUFFICIENT:
                """We couldn't make the hedge with the desired quantity,
                   therefore try to make the hedge with any USDT we have available."""
                
                self.print_log(f"Going to place {HEDGE_SYMBOL} hedge with USDT available...")

                quantity          = round((usdt_available/mark_price), 3)
                notional_quantity = self.get_notional_value(mark_price, quantity, ETH_MIN)
                result            = self.futures_place_short_position(symbol=HEDGE_SYMBOL, quantity=notional_quantity)

            if result != ERROR_MARGIN_INSUFFICIENT:
                self.create_hedge_stop_loss(side=SideType.SIDE_BUY, stop_percent=HEDGE_STOP_PERCENT)



        elif hedge_mode == "Long":
            if short_interest == 0:
                return

            balance = abs(long_interest / short_interest)            
            if balance >= SHORT_LONG_RATIO_LIMIT_PERCENT and balance <= 100:
                """If the open interest on our hedge position is within SHORT_TO_LONG_BALANCE_RATIO of the hedge we want to make, don't make the new hedge"""
                # self.print_log(f"long to short open interest balance is {'{:,.2f}'.format(balance*100)}%")
                return
            elif balance > 100:
                if self.futures_get_position_quantity(HEDGE_SYMBOL) != 0: # check if position exists
                    self.print_log("Rebalancing long interest")
                    long_interest  = round(self.futures_get_open_long_interest_with_leverage(), 1)
                    short_interest = round(abs(self.futures_get_open_short_interest_with_leverage()), 1)                    
                    interest_diff  = long_interest - short_interest
                    
                    # in order to rebalance, we need to close some of our HEDGE_SYMBOL position
                    mark_price = self.futures_get_mark_price(HEDGE_SYMBOL)   # calculate how much we need to short based on open long positions
                    quantity   = round((interest_diff/mark_price), 3)        # calculate quantity of coin to short
                    self.futures_cancel_order(HEDGE_SYMBOL)
                    self.futures_close_long_position(HEDGE_SYMBOL, quantity)
                    self.create_hedge_stop_loss(side=SideType.SIDE_SELL, stop_percent=-HEDGE_STOP_PERCENT)
                    return
            
            mark_price = self.futures_get_mark_price(HEDGE_SYMBOL)    # calculate how much we need to long based on open short positions
            quantity   = round((usdt_amount_to_hedge/mark_price), 3)
            self.futures_cancel_order(HEDGE_SYMBOL)
            
            
            result = ERROR_MARGIN_INSUFFICIENT
            if quantity != 0:
                result = self.futures_place_long_position(symbol=HEDGE_SYMBOL, quantity=quantity)
            
            if result == ERROR_MARGIN_INSUFFICIENT:
                """We couldn't make the hedge with the desired quantity,
                   therefore try to make the hedge with any USDT we have available."""

                self.print_log(f"Going to try to place {HEDGE_SYMBOL} hedge with USDT available...")                
                
                quantity = round((usdt_available/mark_price), 3)
                notional_quantity = self.get_notional_value(mark_price, quantity, ETH_MIN)
                result            = self.futures_place_long_position(symbol=HEDGE_SYMBOL, quantity=notional_quantity)

            if result != ERROR_MARGIN_INSUFFICIENT:
                self.create_hedge_stop_loss(side=SideType.SIDE_SELL, stop_percent=-HEDGE_STOP_PERCENT)



    def close_hedge(self):
        """Closes the HEDGE_SYMBOL position"""
        quantity = self.futures_get_position_quantity(HEDGE_SYMBOL)

        if quantity > 0.0:
            self.futures_close_long_position(HEDGE_SYMBOL, quantity)
        elif quantity < 0.0:
            self.futures_close_short_position(HEDGE_SYMBOL, quantity)
        else:
            self.print_log(f"cannot close {HEDGE_SYMBOL} position because it doesn't exist.")



    def futures_get_hedge_position(self, symbol, hedge_mode):
        """Checks if there is an open position on the symbol we want to hedge"""
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)

            for dictionary in positions:
                if dictionary['symbol'] == symbol:
                    if hedge_mode == "Short":
                        if float(dictionary['positionAmt']) < 0.0:  # SHORT position
                            return True
                    elif hedge_mode == "Long":
                        if float(dictionary['positionAmt']) > 0.0:  # LONG position
                            return True
        except Exception as e:
            self.handle_exception(e, "Could not get hedge position")
        return False


###################################################################################################
### S/L DIFFERENCE  ###
###################################################################################################

    def get_short_long_difference(self):
        """Gets the difference between short and long open positions with leverage factored in"""
        long_interest       = self.futures_get_open_long_interest_with_leverage()
        short_interest      = self.futures_get_open_short_interest_with_leverage()
        difference_interest = abs(short_interest) - long_interest
        return round(difference_interest, 2)




###################################################################################################
### THREADED FUNCTIONS ###
###################################################################################################


    def thread_reopen_orders_threshold(self):
        """If our margin ratio has dropped below MARGIN_RATIO_THRESHOLD, then lets reopen all of our closed orders"""
        while True:
            if self.futures_get_account_margin_ratio() < REOPEN_ORDERS_THRESHOLD:
                self.futures_reopen_all_closed_orders()
                self.has_started_reopen_threshold = True
                break

            if self.exit_event.wait(timeout=2):
                self.has_started_reopen_threshold = True
                break

    
###################################################################################################
### TICK/STEP SIZE ###
###################################################################################################

    def futures_get_tick_and_step_size(self, symbol):
        """Gets the tick and step size for a given symbol.
        Tick size can be used to get the maximum decimal places for price in terms of USDT of an order.
        Step size is the min quantity of coin that we can order"""
        tick_size = None
        step_size = None
        try:
            symbol_info = self.client.get_symbol_info(symbol)
            
            if symbol_info is None:
                """If we couldn't find the data from binance, search the file"""
                # tick_size = self.futures_get_max_precision(symbol)
                # step_size = self.futures_get_symbol_min_trade_quantity(symbol)
                tick_size = float(FUTURES_MAX_PRECISION_DICT[symbol])
                step_size = float(FUTURES_MIN_TRADE_DICT[symbol])
                if tick_size == 1:
                    tick_size = 0
                else:
                    tick_size = len(str(tick_size)) - 2
                return tick_size, step_size

            for filter in symbol_info['filters']:
                if filter['filterType'] == 'PRICE_FILTER':
                    tick_size = float(filter['tickSize'])
                    if tick_size == 1:
                        tick_size = 0
                    else:
                        tick_size = len(str(tick_size)) - 2

                elif filter['filterType'] == 'LOT_SIZE':
                    step_size = float(filter['stepSize'])
                    if step_size == 1:
                        step_size = 0
                    else:
                        step_size = len(str(step_size)) - 2                    
        except Exception as e:
            self.print_log(message=f"Could not get tick and step size for {symbol}", e=e)
        return tick_size, step_size



###################################################################################################
### LIMIT ORDERS ###
###################################################################################################

    def futures_get_open_limit_orders_from_file(self):
        """Returns a list of open orders from LIMIT_ORDERS_FILE. Old orders that are no longer open will not be included."""
        try:
            old_limit_orders       = self.read()
            open_limit_orders_list = list()
            current_open_orders    = self.client.futures_get_open_orders(recvWindow=RECV_WINDOW)

            # Do we need to remove it from the list if the orderId's match or don't match?

            for old_order in old_limit_orders:
                for open_order in current_open_orders:
                    if old_order['orderId'] == open_order['orderId']:
                        open_limit_orders_list.append(old_order)

        except Exception as e:
            self.handle_exception(e, f"could not get open orders from {LIMIT_ORDERS_FILE}")
        return open_limit_orders_list


    def futures_cancel_managed_limit_order(self, symbol, new_limit_price):
        """Creates and manages the data in LIMIT_ORDERS_FILE.
            If the order is still open, cancel it because we are about to make a new limit order which will render our previous limit order useless.
            Return a list of orders that are still open that the AL bot is managing."""

        try:
            # create and manage all the limit orders AL has created
            self.file_create()
            open_limit_orders_list = self.futures_get_open_limit_orders_from_file() # Returns a list of open orders from LIMIT_ORDERS_FILE

            # no orders to cancel
            if len(open_limit_orders_list) == 0:
                return True

            # we only want to cancel the order if the new price if different than the old price
            for open_order in open_limit_orders_list:
                if open_order['symbol'] == symbol and float(open_order['price']) != float(new_limit_price):
                    self.client.futures_cancel_order(symbol=open_order['symbol'], orderId=open_order['orderId'], recvWindow=RECV_WINDOW)
                    self.print_log(f" Cancelled order: {open_order}")
                    return True # cancelled the order
                elif float(open_order['price']) == float(new_limit_price):
                    # self.print_log(f"Not cancelling {symbol} limit order. Current limit price (${open_order['price']}) = New limit price (${new_limit_price})")
                    pass
        except Exception as e:
            self.handle_exception(e, f"could not manage data in {LIMIT_ORDERS_FILE}")
        return False # didn't cancelled order



    def futures_update_limit_orders_file(self, result_list):
        """Truncate LIMIT_ORDERS_FILE file with the new data"""
        try:
            if os.path.exists(LIMIT_ORDERS_FILE):
                self.unhide_file(LIMIT_ORDERS_FILE)
                file = open(LIMIT_ORDERS_FILE, 'w+')
                file.truncate()
                for i in result_list:
                    file.write(str(i)+"\n")
                file.close()
                self.hide_file(LIMIT_ORDERS_FILE)
        except Exception as e:
            self.handle_exception(e, f"could not update {LIMIT_ORDERS_FILE}")                 


    def futures_place_limit_orders(self):
        """Cancel all orders inside of LIMIT_ORDERS_FILE and place new 
            limit orders for all open positions CLOSE_PERCENT higher than entry price.
            LIMIT_ORDERS_FILE contains all of AL's previous limit orders that should be cancelled before putting in new ones."""
        limit_price    = 0
        symbol         = None
        order          = None
        orders_list    = list()

        try:
            open_positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)

            for position in open_positions:
                if float(position['positionAmt']) == NOTHING or position['symbol'] == HEDGE_SYMBOL:
                    continue
                
                symbol         = position['symbol']
                entry_price    = float(position['entryPrice'])
                quantity       = float(position['positionAmt'])
                tick_size, step_size   = self.futures_get_tick_and_step_size(symbol)
                side           = SideType.SIDE_BUY
                limit_price    = entry_price - (entry_price * CLOSE_PERCENT)

                if quantity > 0:
                    limit_price = entry_price + (entry_price * CLOSE_PERCENT)
                    side = SideType.SIDE_SELL

                limit_price = '{:.{precision}f}'.format(limit_price, precision=tick_size)

                # we only want to cancel the order if the new price if different than the old price
                result = self.futures_cancel_managed_limit_order(symbol, limit_price)

                if result:
                    """if there are no open orders that AL is managing, you are free to put in any limit order that you want!"""
                    order = self.futures_create_limit_order(symbol, side, quantity, limit_price)
                    if order != -1:
                        orders_list.append(order)
                    else:
                        continue
                else:
                    # self.print_log(f"Not placing new limit order for {symbol}.")
                    pass

        except Exception as e:
            self.handle_exception(e, f"Could not set limit order for {symbol}.")
        
        if len(orders_list) != 0:
            self.futures_update_limit_orders_file(orders_list)




    def futures_create_limit_order(self, symbol, side, quantity, limit_price):
        try:
            order = self.client.futures_create_order(
                        symbol       = symbol,
                        side         = side,
                        positionSide = PositionSideType.BOTH,
                        type         = OrderType.FUTURE_ORDER_TYPE_LIMIT,
                        quantity     = abs(quantity),
                        price        = limit_price,
                        reduceOnly   = True,
                        timeInForce  = "GTC",
                        recvWindow	 = RECV_WINDOW)

            self.print_log(f"Created limit order: {str(order)}")
            # orders_list.append(order)
            return order
        except Exception as e:
            self.handle_exception(e, f"Could not set limit order for {symbol}")        
            return -1


        

###################################################################################################
### TRANSFERS ###
###################################################################################################

    def futures_to_spot_transfer(self, quantity_to_transfer, symbol="USDT"):
        """Transfer asset from futures wallet to spot wallet
                1: transfer from spot account to USDT-Ⓜ futures account.
                2: transfer from USDT-Ⓜ futures account to spot account."""
        
        try:
            self.client.futures_account_transfer(
                asset            = symbol,
                amount           = quantity_to_transfer,
                type             = 2,
                dualSidePosition = False,
                recvWindow       = RECV_WINDOW)

            self.print_log(f"Moved {symbol} {quantity_to_transfer} from futures to spot wallet")
        except Exception as e:
            self.handle_exception(e, "Futures_to_spot_transfer failed")



    def spot_to_futures_transfer(self, asset, amount):
        """Transfer asset from spot wallet to futures wallet:
                1: transfer from spot account to USDT-Ⓜ futures account.
                2: transfer from USDT-Ⓜ futures account to spot account."""

        # check spot balance before transfer
        balance = self.get_spot_coin_balance(symbol=asset)

        if balance <= NOTHING:
            self.print_log(f"Can't transfer from spot to futures wallet. Balance : {balance}")
            return False

        try:
            self.client.futures_account_transfer(
                asset            = asset,
                amount           = amount,
                type             = 1,
                dualSidePosition = False,
                recvWindow       = RECV_WINDOW)

            self.print_log(f"Moved {asset} {amount} from spot to futures wallet")
        except Exception as e:
            self.handle_exception(e, f"Could not transfer {asset} {amount} from spot to futures wallet")
            return False
        return True


    def spot_coin_to_usdt_futures_transfer(self) -> bool:
        """
        Loops through all our spot coins and finds the one worth the least in terms of USDT
        Market sells that coin for USDT
        Transfers USDT amount to futures account in order to lower margin ratio.
        """

        spot_coin_dict = self.get_all_spot_coins_and_values()

        # choose a spot coin with the least amount of money
        smallest_coin, quantity = self.get_smallest_spot_coin(spot_coin_dict)

        smallest_coin += USDT

        if quantity > NOTHING:
            # sell it for USDT
            self.client.order_market_sell(symbol=smallest_coin, quantity=quantity, recvWindow=RECV_WINDOW)
        
        # get the amount of USDT in our spot account
        usdt_quantity = self.get_spot_coin_balance(USDT)

        if usdt_quantity > NOTHING:
            # transfer to futures account, returns True if successful, False if unsuccessful
            return self.spot_to_futures_transfer(asset=USDT, amount=usdt_quantity)

        # we made no transfer
        return False


###################################################################################################
### ORDERS ###
###################################################################################################

    def futures_close_all_open_orders(self):
        """Closes all open orders for all futures symbols"""
        count       = 0
        symbol_list = list()

        # store all symbols that have open orders in list
        for dictionary in self.open_orders:
            symbol_list.append(dictionary['symbol'])
        
        try:
            open_orders_list = list()
            self.open_orders = self.client.futures_get_open_orders(recvWindow=RECV_WINDOW)
            
            for dictionary in self.open_orders:
                open_orders_list.append(dictionary['symbol'])

            while len(open_orders_list) > 0:
                # cancel all open orders
                for symbol in symbol_list:
                    if symbol != HEDGE_SYMBOL: # Don't close our HEDGE_SYMBOL orders
                        self.client.futures_cancel_all_open_orders(symbol=symbol, recvWindow=RECV_WINDOW)
                        open_orders_list.remove(symbol)
                        self.print_log(f"closed {symbol} order")
                        count += 1
                    elif symbol == HEDGE_SYMBOL:
                        open_orders_list.remove(symbol)
                
                # prevents an infinite while loop
                if count >= 100000:
                    self.print_log("Too many open orders to close")
                    break
        except Exception as e:
            self.handle_exception(e, "Could not close all open orders")



    def futures_get_all_open_orders(self):
        """Get all open orders. Returns a list of dictionaries containing the open orders"""
        open_orders = list()
        try:
            open_orders = self.client.futures_get_open_orders(recvWindow=RECV_WINDOW)
        except Exception as e:
            self.handle_exception(e, "Could not get all open orders")
        return open_orders


    def futures_save_all_open_orders(self):
        """Saves all open orders to variable, then writes them all to a file"""
        if not self.has_saved_open_orders:
            self.open_orders = self.futures_get_all_open_orders()
            try:
                """if OPEN_ORDERS_FILE already exists and is hidden, we have to unhide it first before we write over it."""
                if os.path.exists(os.getcwd() + "\\" + OPEN_ORDERS_FILE):
                        self.unhide_file(OPEN_ORDERS_FILE)

                with open(OPEN_ORDERS_FILE, 'w+') as file:
                    for order in self.open_orders:
                        file.write(str(order))
                        file.write("\n")

                self.hide_file(OPEN_ORDERS_FILE)
                self.print_log(f"Saved all open orders to {OPEN_ORDERS_FILE}")
                self.has_saved_open_orders = True
            except Exception as e:
                self.handle_exception(e, "Could not save open orders to file")
                self.has_saved_open_orders = False  



    def futures_get_total_open_orders_value(self):
        """Get the total amount of USDT being used in all of our open orders"""
        total_open_orders = 0
        try:
            symbol_dict = self.futures_get_all_open_interests()
            for symbol, value in symbol_dict.items():
                open_order = self.client.futures_get_open_orders(symbol=symbol, recvWindow=RECV_WINDOW)
                for dictionary in open_order:
                    total_open_orders += float(dictionary['price']) * float(dictionary['origQty'])  
        except Exception as e:
            self.handle_exception(e, "Could not get total open orders value")
        return round(total_open_orders, 1)


    def futures_reopen_all_closed_orders(self):
        """Reopens orders that were closed when margin ratio was above MARGIN_RATIO_THRESHOLD.
            If the positions were closed then don't put the associated orders back in"""
        try:
            # only put the orders back in that still have an open position
            open_positions_list = self.futures_get_all_open_positions()

            with open(OPEN_ORDERS_FILE, 'r') as file:
                for order in file.readlines():
                    ord = literal_eval(order)
                    if ord['symbol'] in open_positions_list:
                        self.client.futures_create_order(
                            symbol        = ord['symbol'],
                            side          = ord['side'],
                            type          = ord['type'],
                            price         = ord['price'],
                            quantity      = ord['origQty'],
                            timeInForce   = ord['timeInForce'],
                            reduceOnly    = ord['reduceOnly'],
                            closePosition = ord['closePosition'],
                            positionSide  = ord['positionSide'],
                            recvWindow    = RECV_WINDOW)

                        self.print_log(f"Reopened {ord['symbol']} {float(ord['origQty'])} {'${:,.4f}'.format(float(ord['price']))} order")
                    else:
                        # self.print_log(f"Not reopening {ord['symbol']} {float(ord['origQty'])} {'${:,.4f}'.format(float(ord['price']))} because position is not currently open")
                        pass
            self.has_saved_open_orders = False
        except Exception as e:
            self.handle_exception(e, "Could not reopen all closed orders")



    def futures_cancel_order(self, symbol):
        """Cancels all open orders for a given symbol"""
        try:
            # quantity = self.futures_get_position_quantity(symbol)
            # if quantity == 0.0:
            #     self.print_log(f"{symbol} order is not currently open")
            #     return

            is_order_open = False
            open_orders = self.futures_get_all_open_orders()

            for dictionary in open_orders:
                if dictionary['symbol'] == symbol:
                    is_order_open = True
                    break
            
            if is_order_open:
                self.client.futures_cancel_all_open_orders(symbol=symbol, recvWindow=RECV_WINDOW)
                self.print_log(f"Cancelled {symbol} order")
        except Exception as e:
            self.handle_exception(e, f"Could not close {symbol} order")


###################################################################################################
### SPOT COIN ###
###################################################################################################

    def get_spot_coin_balance(self, symbol):
        """Gets owned quantity of a spot coin"""
        balance = 0.0
        try:
            balances = self.client.get_account(recvWindow=RECV_WINDOW)['balances']
            for dictionary in balances:
                if dictionary['asset'] == symbol:
                    balance = float(dictionary['free']) + float(dictionary['locked'])
                    break
        except Exception as e:
            self.handle_exception(e, f"Could not get spot coin balance")
        return balance


    def get_all_spot_coins(self):
        """Gets all owned spot coins"""
        spot_coin_list = list()
        try:
            balances = self.client.get_account(recvWindow=RECV_WINDOW)['balances']
            for dictionary in balances:
                if (float(dictionary['free']) + float(dictionary['locked'])) > NOTHING:
                    spot_coin_list.append(dictionary['symbol'])
        except Exception as e:
            self.handle_exception(e, f"Could not get all spot coins")                
        return spot_coin_list


    def get_all_spot_coins_and_values(self):
        """Gets all spot coins we own and their total worth. Returns a dict [symbol, usdt_value]"""
        spot_coin_dict   = dict()
        try:
            account_balances = self.client.get_account(recvWindow=RECV_WINDOW)['balances']

            # Add up all stable coins that are 1:1 with the US dollar
            for dictionary in account_balances:
                if dictionary['asset'] in STABLE_COINS:
                    if float(dictionary['free']) > NOTHING or float(dictionary['locked']) > NOTHING:
                        spot_coin_dict[dictionary['asset']] = float(dictionary['free']) + float(dictionary['locked'])

            # add non-stable coins
            for dictionary in account_balances:
                if dictionary['asset'] not in STABLE_COINS:
                    if (float(dictionary['free']) + float(dictionary['locked'])) > NOTHING:
                        if dictionary['asset'][0] == 'L' and dictionary['asset'][1] == 'D': # coins in savings account will start with a "LD" and we don't want to count those here
                            continue

                        quantity = float(dictionary['free']) + float(dictionary['locked'])
                        symbol   = dictionary['asset'] + "USDT"
                        
                        try:
                            # even when this works, it takes too long to iterate over all coins
                            symbol_price = self.client.get_symbol_ticker(symbol=symbol)
                            symbol = symbol_price['symbol']
                            symbol_price = float(symbol_price['price'])
                            symbol_price = round(symbol_price, 2)
                        except Exception as e:
                            self.handle_exception(e, f"could not get spot coin {symbol} value")
                            continue
                        
                        coin_value_in_usdt                  = float(symbol_price) * quantity
                        spot_coin_dict[dictionary['asset']] = round(coin_value_in_usdt, 3)
        except Exception as e:
            self.handle_exception(e, "Could not get all spot coins and values")
        return spot_coin_dict



    def get_smallest_spot_coin(self, spot_coin_dict):
        """Finds a spot coin that we own that is worth the least in terms of USDT"""
        smallest_amount = 0.0
        quantity        = 0.0
        smallest_symbol = ""

        # set the initial value of smallest_amount to the very first coin in the dict
        for key, value in spot_coin_dict.items():
            # convert 'free' to usdt amount
            smallest_symbol = key
            smallest_amount = self.futures_get_mark_price(key)
            break

        # find the coin with the smallest amount of money in it
        for key, value in spot_coin_dict.items():
            if float(value) < smallest_amount:
                smallest_symbol = key
                smallest_amount = self.futures_get_mark_price(key)
                quantity        = value
        return smallest_symbol, quantity


###################################################################################################
### ACCOUNT VALUES ###
###################################################################################################

    def binance_account_get_total_value(self):
        """Gets binance total account value. If user has many spot coins, runtime could take a long time"""
        try:
            spot_account_dict        = self.get_all_spot_coins_and_values()
            futures_account          = self.client.futures_account(recvWindow=RECV_WINDOW)
            lending_account_value    = float(self.client.get_lending_account(recvWindow=RECV_WINDOW)['totalAmountInUSDT'])
            spot_account_total_value = 0.0

            # This includes unrealized profit (takes the absolute value of unrealized profit and adds it to the total)
            futures_wallet_total_balance = round(float(futures_account['totalWalletBalance']), 2)
            if len(spot_account_dict.keys()) > NOTHING:
                for value in spot_account_dict.values():
                    spot_account_total_value += float(value)
            spot_account_total_value = round(spot_account_total_value, 2)
            total_account_value      = spot_account_total_value + futures_wallet_total_balance + lending_account_value
        except Exception as e:
            self.handle_exception(e, "Could not get binance account total")
            return -1
        return round(total_account_value)


    def futures_get_available_tether(self):
        """Gets available tether in futures wallet"""
        usdt_quantity = 0.0
        try:
            assets = self.client.futures_account(recvWindow=RECV_WINDOW)['assets']
            for dictionary in assets:
                if dictionary['asset'] == USDT:
                    usdt_quantity = dictionary['maxWithdrawAmount']
                    break
        except Exception as e:
            self.handle_exception(e, "Could not get available tether")
            return -1
        return round(float(usdt_quantity))


    def futures_get_account_margin_ratio(self):
        """Gets binance futures account margin ratio"""
        current_margin_ratio = 0.0
        
        try:
            futures_account = self.client.futures_account(recvWindow=RECV_WINDOW)
            if float(futures_account['totalMarginBalance']) != 0.0:
                current_margin_ratio = ( float(futures_account['totalMaintMargin']) / float(futures_account['totalMarginBalance']) ) * 100
        except Exception as e:
            self.handle_exception(e, "Could not get current margin ratio")
            return -1         
        return round(current_margin_ratio, 2)


    def futures_get_wallet_value(self):
        """Gets USDT-Ⓜ futures wallet value in terms of USDT"""
        try:
            futures_account              = self.client.futures_account(recvWindow=RECV_WINDOW)
            futures_wallet_total_balance = round(float(futures_account['totalWalletBalance']), 2)
        except Exception as e:
            self.handle_exception(e, "Could not get futures account value")
            return -1
        return futures_wallet_total_balance


###################################################################################################
### OPEN INTERESTS ###
###################################################################################################
    def futures_get_all_open_interests(self):
        """Gets the values of all open positions and returns a dict"""
        price_dict = dict()
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if float(dictionary['notional']) != NOTHING:
                    price_dict[dictionary['symbol']] = float(dictionary['notional'])
        except Exception as e:
            self.handle_exception(e, "Could not get futures all open interests")
        return price_dict


    def futures_get_largest_open_interest(self, open_interest_dict):
        """Finds the open position worth the most amount of money"""
        largest_open_interest = 0.0
        largest_open_symbol = ""
        for key, value in open_interest_dict.items():
            if float(value) > largest_open_interest:
                largest_open_interest = value
                largest_open_symbol   = key
        return largest_open_symbol


    def futures_get_open_interest_total(self):
        """Gets the total amount of all open positions by adding them all together"""
        open_interest = 0.0
        
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if float(dictionary['positionAmt']) != NOTHING:  # for any open position
                    open_interest += abs(float(dictionary['positionAmt']) * float(dictionary['entryPrice'])) #/ float(dictionary['leverage'])
        except Exception as e:
            self.handle_exception(e, "Could not get futures open interest total")
        return round(open_interest, 2)




###################################################################################################
### UTILITY/ETC... ###
###################################################################################################

    def futures_get_mark_price(self, symbol):
        """Get the mark price (current price) for a symbol"""
        markprice = 0.0
        
        if symbol in STABLE_COINS:
            return 1.0
        try:
            markprice = self.client.futures_mark_price(symbol=symbol, recvWindow=RECV_WINDOW)['markPrice']
            markprice = float(markprice)
        except Exception as e:
            self.handle_exception(e, f"Could not get futures mark price for {symbol}")
        return markprice



    def futures_get_best_unrealized_roi_position(self):
        """get all assets with positive unrealized profit"""
        highest       = -9999999999.9
        symbol        = ""
        non_zero_dict = dict()

        try:
            positions = self.client.futures_account(recvWindow=RECV_WINDOW)['positions'] 
            
            for dictionary in positions:
                if dictionary['positionAmt'] == NOTHING or dictionary['symbol'] == "BTCDOMUSDT":
                    continue

                current_roi            = 0
                entry_position_value   = float(dictionary['entryPrice']) * float(dictionary['positionAmt'])
                current_mark_value = self.futures_get_mark_price(dictionary['symbol']) * float(dictionary['positionAmt'])
                
                if current_mark_value != NOTHING:
                    current_roi = ((current_mark_value / entry_position_value) - 1) * 100
                else:
                    continue

                if current_roi >= CLOSE_PERCENT:
                    if dictionary['symbol'] != HEDGE_SYMBOL:
                        non_zero_dict[dictionary['symbol']] = float(dictionary["unrealizedProfit"])
            
            for key, value in non_zero_dict.items():
                if value > highest:
                    symbol  = key
                    highest = value
        except Exception as e:
            self.handle_exception(e, "Could not get largest positive unrealized position")
        return symbol


    def futures_change_margin_type(self, symbol, margin_type):
        """Changes margin type to Isolated or Cross.
            If we are using cross and the symbol is isolated, close the position.
            If there are open orders on the symbol, close them."""
        try:
            self.client.futures_change_margin_type(symbol=symbol, marginType=margin_type, recvWindow=RECV_WINDOW)
        except Exception as e:
            if str(e.code) == ERROR_MARGIN_CHANGE_OPEN_ORDERS2: #or str(e.code) == ERROR_MARGIN_CHANGE_OPEN_ORDERS1 or
                self.futures_cancel_order(symbol)
            elif str(e.code) == ERROR_MARGIN_CHANGE_OPEN_POSITION:
                position_type = self.futures_get_position_type(symbol)
                quantity      = self.futures_get_position_quantity(symbol)
                if position_type == "Long":
                    self.futures_close_long_position(symbol, quantity)
                else:
                    self.futures_close_short_position(symbol, quantity)

                self.futures_cancel_order(symbol)
            elif str(e.code) == ERROR_MARGIN_CHANGE_OPEN_ORDERS1:
                """symbol is already set to CROSS and not ISOLATED so there is nothing left to do but return"""
                pass
            else:
                self.handle_exception(e, f"Could not change {symbol} margin type to {margin_type}")


    def get_notional_value(self, mark_price, quantity_to_sell, min_quantity):
        """if the quantity of coin we want to trade is less than $5 (futures minimum),
            then find and set the min amount to trade at $5 in terms of the quantity of coin"""
        i = min_quantity
        result = quantity_to_sell * mark_price
        if result < FUTURES_NOTIONAL_MIN:
            while result < FUTURES_NOTIONAL_MIN:
                i += min_quantity
                result = i * mark_price
                quantity_to_sell = i
        return quantity_to_sell



###################################################################################################
### PnL ###
###################################################################################################

    def futures_get_realized_profit(self):
        """Gets profit made for the last 24 hours in usdt"""
        realizedPnl = 0
        try:
            futures_account_trades = self.client.futures_account_trades(recvWindow=RECV_WINDOW)
            for dictionary in futures_account_trades:
                if float(dictionary['realizedPnl']) > NOTHING: 
                    realizedPnl += float(dictionary['realizedPnl'])
        except Exception as e:
            self.handle_exception(e, "Could not get futures realized pnl")
        return round(realizedPnl, 2)


    def futures_get_total_unrealized_profit(self):
        """Gets the unrealized profit for all open positions"""
        unrealizedPnl = 0
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if float(dictionary['unRealizedProfit']) != NOTHING:
                    unrealizedPnl += float(dictionary['unRealizedProfit'])
        except Exception as e:
            self.handle_exception(e, "Could not get futures realized pnl")
        return unrealizedPnl



    def futures_get_total_unrealized_roi(self):
        """Gets the unrealized ROI for all open positions"""
        total_unrealized_roi = 0
        total_mark_value     = 0
        total_entry_value    = 0
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:

                if float(dictionary['positionAmt']) == NOTHING:
                    continue

                mark_price      = float(self.futures_get_mark_price(dictionary['symbol'])) # gets current price for coin
                position_amount = abs(float(dictionary['positionAmt']))                    # quantity of coin we own
                entry_price     = float(dictionary['entryPrice'])                          # the entry price of the coin we bought

                entry_value = entry_price * position_amount
                mark_value  = mark_price  * position_amount

                total_entry_value += entry_value
                total_mark_value  += mark_value

            if total_entry_value != 0:
                total_unrealized_roi = ((total_mark_value / total_entry_value) - 1) * 100
            self.print_log(f"total_unrealized_roi: {'{:,.4f}%'.format(float(total_unrealized_roi))}")
        except Exception as e:
            self.handle_exception(e, "Could not get futures realized pnl")
        return total_unrealized_roi



    def futures_get_todays_profit(self):
        """Gets USDT made in the last 24 hours"""
        todays_pnl  = 0.0
        one_day_in_milliseconds = 86400000
        now_milliseconds = int(time.time()*1000) # milliseconds since the epoch
        yesterday_milliseconds = now_milliseconds - one_day_in_milliseconds

        try:
            futures_income_history = self.client.futures_income_history(
                                        limit      = 1000, 
                                        incomeType = "REALIZED_PNL", 
                                        startTime  = yesterday_milliseconds, 
                                        endTime    = now_milliseconds, 
                                        recvWindow = RECV_WINDOW)

            for dictionary in futures_income_history:
                if float(dictionary['income']) != NOTHING:
                    todays_pnl += float(dictionary['income'])                
        except Exception as e:
            self.handle_exception(e,"Could not get todays pnl")
        return round(todays_pnl, 2)



###################################################################################################
### TRADES ###
###################################################################################################

    def futures_get_trades(self):
        """Gets all trades made for the last 24 hours"""
        trade_list = list()
        try:
            account_trades      = self.client.futures_account_trades(limit=50, recvWindow=RECV_WINDOW)
            account_trades_list = list(account_trades)
            account_trades_list.reverse()
            for dictionary in account_trades_list:
                if float(dictionary['realizedPnl']) > NOTHING: 
                    trade_list.append(dictionary)
        except Exception as e:
            self.handle_exception(e, "Could not get futures trades")
        return trade_list




###################################################################################################
### WITHDRAWLS/DEPOSITS ###
###################################################################################################

    def get_all_withdraw_history(self):
        try:
            withdraws = self.client.get_withdraw_history(recvWindow=RECV_WINDOW)
            for dictionary in withdraws:
                print(dictionary)
        except Exception as e:
            self.handle_exception(e, "Could not get all withdrawl history")


    def get_all_deposit_history(self):
        try:
            deposits = self.client.get_deposit_history(recvWindow=RECV_WINDOW)
            for dictionary in deposits:
                print(dictionary)
        except Exception as e:
            self.handle_exception(e, "Could not get all deposit history")


    def withdraw(self, symbol, address, amount):
        try:
            self.client.withdraw(coin=symbol, address=address, amount=amount, recvWindow=RECV_WINDOW)
        except Exception as e:
            self.handle_exception(e, f"Could not withdraw {symbol} {amount}")



###################################################################################################
### POSITIONS  ###
###################################################################################################


    # NUKE!!! CLOSE ALL POSITIONS
    def futures_close_all_positions(self):
        """DANGER: This closes all open positions. This will nuke your entire account!"""
        try:
            self.print_log("###### Nuke Triggered! #####")
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)

            for dictionary in positions:
                if float(dictionary['positionAmt']) > NOTHING:
                    self.futures_close_long_position(dictionary['symbol'], float(dictionary['positionAmt']))
                elif float(dictionary['positionAmt']) < NOTHING:
                    self.futures_close_short_position(dictionary['symbol'], float(dictionary['positionAmt']))
            self.print_log("closed all open positions")
        except Exception as e:
            self.handle_exception(e, "Could not close all open positions")


    def futures_get_all_open_positions(self):
        """Get all open positions"""
        open_positions_list = list()
        try:
            positions = self.client.futures_position_information(recvWindow=RECV_WINDOW)
            for dictionary in positions:
                if float(dictionary['positionAmt']) != NOTHING:
                    open_positions_list.append(dictionary['symbol'])
        except Exception as e:
            self.handle_exception(e, "Could not get all open positions")
        return open_positions_list



    def futures_get_position_type(self, symbol):
        """Figure out if our position is a long or short"""
        position_type = "Short"
        try:
            positions = self.client.futures_account(recvWindow=RECV_WINDOW)['positions']
            for dictionary in positions:
                if dictionary["symbol"] == symbol:
                    if float(dictionary['positionAmt']) > NOTHING:
                        position_type = "Long"
                        break
        except Exception as e:
            self.handle_exception(e, "Could not get futures position type")
        return position_type




###################################################################################################
### FOR TRADING VIEW PURPOSES  ###
###################################################################################################


    def futures_get_all_symbols(self):
        """Get all futures symbols on binance and return them as a list with PERP added on the end"""
        exchange    = self.client.futures_exchange_info()['symbols']
        symbol_list = list()
        for dictionary in exchange:
            symbol_list.append(dictionary['symbol'] + "PERP")
        return symbol_list



    def futures_write_symbols_to_file(self):
        """Writes all of Binance futures symbols to file"""
        symbol_list = self.futures_get_all_symbols()
        with open("binance_futures_symbols.txt", "w+") as file:
            for symbol in symbol_list:
                file.write(symbol+"\n")



###################################################################################################
### ANTI-LIQUIDATION PROCEDURE ###
###################################################################################################
    def anti_liquidation_procedure(self):

        # save and close all open orders
        if not self.al_procedure_active:
            self.futures_save_all_open_orders()
            self.futures_close_all_open_orders()
            self.al_procedure_active = True
        
        
        # place limit orders CLOSE_PERCENT higher than entry_price
        if datetime.datetime.now() >= self.limit_order_future: 
            """limit the number of orders to create/close by 30 seconds"""
            self.limit_order_future = datetime.timedelta(minutes=0.5) + datetime.datetime.now()
            self.futures_place_limit_orders()


        if not self.has_started_reopen_threshold:
            t2 = Thread(target=self.thread_reopen_orders_threshold)
            t2.start()
            self.has_started_reopen_threshold = True

        # delay the time between closing all positive unrealized positions and creating the hedge
        if self.exit_event.wait(timeout=2): return

        current_margin_ratio = self.futures_get_account_margin_ratio()
        
        if current_margin_ratio >= MARGIN_RATIO_THRESHOLD:
            self.create_hedge()
        elif current_margin_ratio < MARGIN_RATIO_THRESHOLD:
            self.close_hedge()
            self.futures_cancel_order(HEDGE_SYMBOL)

        # If we have closed all positions except for the hedge, close the hedge
        open_positions = self.futures_get_all_open_positions()

        if len(open_positions) == 1:
            if HEDGE_SYMBOL in open_positions:
                self.close_hedge()
                self.futures_cancel_order(HEDGE_SYMBOL)                