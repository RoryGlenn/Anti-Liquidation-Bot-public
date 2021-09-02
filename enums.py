from log           import Log
from config_parser import ConfigParser

g_cfg_dict = ConfigParser(Log()).parse_config_file()                                       # Get the values from the config file


RECV_WINDOW                    = 10000                                                     # 10 seconds for recv window
FLEXIBLE_SAVINGS_USDT_MIN      = 0.10                                                      # 10 cents minimum in order to transfer USDT into flexible savings
USDT_TRANSFER_MIN              = 0.0000001                                                 # Lowest amount we can transfer USDT from futures to spot wallet
BUSDUSDT_MIN                   = 10                                                        # $10 is the min to buy BUSD with USDT
RAKE_THREAD_WAIT_TIME          = 10                                                        # Number of seconds for the rake thread to wait before checking for a new trade
ETH_MIN                        = 0.001                                                     # min amount of ETH we can buy
BNB_MIN                        = 0.01
BNB_BUY_MIN                    = 11.0                                                      # the minimum is really $10 but we need 11 to cover any extra fees
NOTHING                        = 0.0                                                       # You're broke!
FUTURES_NOTIONAL_MIN           = 5                                                         # $5 is the absolute lowest amount we can trade on binance futures
BINANCE_CLIENT_RESET_TIME      = 20                                                        # Every 20 min reset the binance client to avoid OS error

STABLE_COINS                   = ['USDT', 'BUSD', 'PAX', 'USDC', 'USD', 'TUSD', 'DAI', 'UST', 'HUSD', 'USDN', 'GUSD', 'FEI', 'LUSD', 'FRAX', 'SUSD', 'USDX', 'MUSD', 'USDK', 'USDS', 'USDP', 'RSV',  'USDQ', 'USDEX']
FUTURES_MIN_TRADE_DICT         = {'BTCUSDT': '0.001', 'ETHUSDT': '0.001', 'BCHUSDT': '0.001', 'XRPUSDT': '0.1', 'EOSUSDT': '0.1', 'LTCUSDT': '0.001', 'TRXUSDT': '1', 'ETCUSDT': '0.01', 'LINKUSDT': '0.01', 'XLMUSDT': '1', 'ADAUSDT': '1', 'XMRUSDT': '0.001', 'DASHUSDT': '0.001', 'ZECUSDT': '0.001', 'XTZUSDT': '0.1', 'BNBUSDT': '0.01', 'ATOMUSDT': '0.01', 'ONTUSDT': '0.1', 'IOTAUSDT': '0.1', 'BATUSDT': '0.1', 'VETUSDT': '1', 'NEOUSDT': '0.01', 'QTUMUSDT': '0.1', 'IOSTUSDT': '1', 'THETAUSDT': '0.1', 'ALGOUSDT': '0.1', 'ZILUSDT': '1', 'KNCUSDT': '1', 'ZRXUSDT': '0.1', 'COMPUSDT': '0.001', 'OMGUSDT': '0.1', 'DOGEUSDT': '1', 'SXPUSDT': '0.1', 'KAVAUSDT': '0.1', 'BANDUSDT': '0.1', 'RLCUSDT': '0.1', 'WAVESUSDT': '0.1', 'MKRUSDT': '0.001', 'SNXUSDT': '0.1', 'DOTUSDT': '0.1', 'DEFIUSDT': '0.001', 'YFIUSDT': '0.001', 'BALUSDT': '0.1', 'CRVUSDT': '0.1', 'TRBUSDT': '0.1', 'YFIIUSDT': '0.001', 'RUNEUSDT': '1', 'SUSHIUSDT': '1', 'SRMUSDT': '1', 'BZRXUSDT': '1', 'EGLDUSDT': '0.1', 'SOLUSDT': '1', 'ICXUSDT': '1', 'STORJUSDT': '1', 'BLZUSDT': '1', 'UNIUSDT': '1', 'AVAXUSDT': '1', 'FTMUSDT': '1', 'HNTUSDT': '1', 'ENJUSDT': '1', 'FLMUSDT': '1', 'TOMOUSDT': '1', 'RENUSDT': '1', 'KSMUSDT': '0.1', 'NEARUSDT': '1', 'AAVEUSDT': '0.1', 'FILUSDT': '0.1', 'RSRUSDT': '1', 'LRCUSDT': '1', 'MATICUSDT': '1', 'OCEANUSDT': '1', 'CVCUSDT': '1', 'BELUSDT': '1', 'CTKUSDT': '1', 'AXSUSDT': '1', 'ALPHAUSDT': '1', 'ZENUSDT': '0.1', 'SKLUSDT': '1', 'GRTUSDT': '1', '1INCHUSDT': '1', 'AKROUSDT': '1', 'CHZUSDT': '1', 'SANDUSDT': '1', 'ANKRUSDT': '1', 'LUNAUSDT': '1', 'BTSUSDT': '1', 'LITUSDT': '0.1', 'UNFIUSDT': '0.1', 'DODOUSDT': '0.1', 'REEFUSDT': '1', 'RVNUSDT': '1', 'SFPUSDT': '1', 'XEMUSDT': '1', 'COTIUSDT': '1', 'CHRUSDT': '1', 'MANAUSDT': '1', 'ALICEUSDT': '0.1', 'HBARUSDT': '1', 'ONEUSDT': '1', 'LINAUSDT': '1', 'STMXUSDT': '1', 'DENTUSDT': '1', 'CELRUSDT': '1', 'HOTUSDT': '1', 'MTLUSDT': '1', 'OGNUSDT': '1', 'BTTUSDT': '1', 'NKNUSDT': '1', 'SCUSDT': '1', 'DGBUSDT': '1', '1000SHIBUSDT': '1', 'ICPUSDT': '0.01', 'BAKEUSDT': '1', 'GTCUSDT': '0.1'}
FUTURES_MAX_PRECISION_DICT     = {'BTCUSDT': '0.01', 'ETHUSDT': '0.01', 'BCHUSDT': '0.01', 'XRPUSDT': '0.0001', 'EOSUSDT': '0.001', 'LTCUSDT': '0.01', 'TRXUSDT': '0.00001', 'ETCUSDT': '0.001', 'LINKUSDT': '0.001', 'XLMUSDT': '0.00001', 'ADAUSDT': '0.00010', 'XMRUSDT': '0.01', 'DASHUSDT': '0.01', 'ZECUSDT': '0.01', 'XTZUSDT': '0.001', 'BNBUSDT': '0.010', 'ATOMUSDT': '0.001', 'ONTUSDT': '0.0001', 'IOTAUSDT': '0.0001', 'BATUSDT': '0.0001', 'VETUSDT': '0.000010', 'NEOUSDT': '0.001', 'QTUMUSDT': '0.001', 'IOSTUSDT': '0.000001', 'THETAUSDT': '0.0010', 'ALGOUSDT': '0.0001', 'ZILUSDT': '0.00001', 'KNCUSDT': '0.00100', 'ZRXUSDT': '0.0001', 'COMPUSDT': '0.01', 'OMGUSDT': '0.0001', 'DOGEUSDT': '0.000010', 'SXPUSDT': '0.0001', 'KAVAUSDT': '0.0001', 'BANDUSDT': '0.0001', 'RLCUSDT': '0.0001', 'WAVESUSDT': '0.0010', 'MKRUSDT': '0.10', 'SNXUSDT': '0.001', 'DOTUSDT': '0.001', 'DEFIUSDT': '0.1', 'YFIUSDT': '1', 'BALUSDT': '0.001', 'CRVUSDT': '0.001', 'TRBUSDT': '0.010', 'YFIIUSDT': '0.1', 'RUNEUSDT': '0.0010', 'SUSHIUSDT': '0.0010', 'SRMUSDT': '0.0010', 'BZRXUSDT': '0.0001', 'EGLDUSDT': '0.010', 'SOLUSDT': '0.0010', 'ICXUSDT': '0.0001', 'STORJUSDT': '0.0001', 'BLZUSDT': '0.00001', 'UNIUSDT': '0.0010', 'AVAXUSDT': '0.0010', 'FTMUSDT': '0.000010', 'HNTUSDT': '0.0010', 'ENJUSDT': '0.00010', 'FLMUSDT': '0.0001', 'TOMOUSDT': '0.0001', 'RENUSDT': '0.00001', 'KSMUSDT': '0.010', 'NEARUSDT': '0.0001', 'AAVEUSDT': '0.010', 'FILUSDT': '0.001', 'RSRUSDT': '0.000001', 'LRCUSDT': '0.00001', 'MATICUSDT': '0.00010', 'OCEANUSDT': '0.00001', 'CVCUSDT': '0.00001', 'BELUSDT': '0.00010', 'CTKUSDT': '0.00100', 'AXSUSDT': '0.00100', 'ALPHAUSDT': '0.00010', 'ZENUSDT': '0.001', 'SKLUSDT': '0.00001', 'GRTUSDT': '0.00001', '1INCHUSDT': '0.0001', 'AKROUSDT': '0.00001', 'CHZUSDT': '0.00001', 'SANDUSDT': '0.00001', 'ANKRUSDT': '0.000010', 'LUNAUSDT': '0.0010', 'BTSUSDT': '0.00001', 'LITUSDT': '0.001', 'UNFIUSDT': '0.001', 'DODOUSDT': '0.001', 'REEFUSDT': '0.000001', 'RVNUSDT': '0.00001', 'SFPUSDT': '0.0001', 'XEMUSDT': '0.0001', 'COTIUSDT': '0.00001', 'CHRUSDT': '0.0001', 'MANAUSDT': '0.0001', 'ALICEUSDT': '0.001', 'HBARUSDT': '0.00001', 'ONEUSDT': '0.00001', 'LINAUSDT': '0.00001', 'STMXUSDT': '0.00001', 'DENTUSDT': '0.000001', 'CELRUSDT': '0.00001', 'HOTUSDT': '0.000001', 'MTLUSDT': '0.0001', 'OGNUSDT': '0.0001', 'BTTUSDT': '0.000001', 'NKNUSDT': '0.00001', 'SCUSDT': '0.000001', 'DGBUSDT': '0.00001', '1000SHIBUSDT': '0.000001', 'ICPUSDT': '0.01', 'BAKEUSDT': '0.0001', 'GTCUSDT': '0.001', 'ETHBUSD': '0.01', 'BTCUSDT0924': '0.1', 'ETHUSDT0924': '0.01', 'BTCDOMUSDT': '0.1', 'KEEPUSDT': '0.0001'}

USDT                           = "USDT"                                                    # Just to make things a little bit easier on the eyes
BUSDUSDT                       = "BUSDUSDT"                                                # Just to make things a little bit easier on the eyes
MARKET                         = "MARKET"                                                  # Just to make things a little bit easier on the eyes
BNB                            = "BNB"                                                     # Just to make things a little bit easier on the eyes
ISOLATED                       = "ISOLATED"                                                # Just to make things a little bit easier on the eyes
CROSS                          = "CROSSED"                                                 # Just to make things a little bit easier on the eyes

ERROR_MARGIN_INSUFFICIENT          = "-2019"                                               
ERROR_NOTIONAL                     = "-4164"                                                # Order's notional must be no smaller than 5.0 (unless you choose reduce only)
ERROR_TIME                         = "-1021"                                                # Timestamp for this request was 1000ms ahead of the server's time.
ERROR_REDUCE_ONLY                  = "-2022"
ERROR_MARGIN_CHANGE_OPEN_POSITION  = "-4048"
ERROR_MARGIN_CHANGE_OPEN_ORDERS1   = "-4046"
ERROR_MARGIN_CHANGE_OPEN_ORDERS2   = "-4047"

OPEN_ORDERS_FILE               = "logs\\open_orders.txt"                                   # All open orders will be saved to this file
RAKED_TRADES_FILE              = "logs\\raked_trades.txt"                                  # All raked trades will be saved to this file
LIMIT_ORDERS_FILE              = "logs\\limit_orders.txt"                                  # All limit orders the bot makes are saved here
FUTURES_MIN_TRADE_AMOUNTS      = "futures_min_trade_amounts.txt"
FUTURES_MAX_PRECISION_FILE     = "futures_max_precision.txt"

TEXT                           = False                                                     # Turns text messages on or off when current_margin_ratio >= MARGIN_RATIO_THRESHOLD
PHONE_CALL                     = False                                                     # Turns phone call on or off when current_margin_ratio >= MARGIN_RATIO_THRESHOLD
RAKE                           = False                                                     # Turns Rake on or off
BUY_BNB                        = False                                                     # Turns bnb_resupply on or off

MARGIN_RATIO_THRESHOLD         = float(g_cfg_dict['margin_ratio_threshold'])               # when to activate anti-liquidation procedures
RAKE_PERCENT                   = float(g_cfg_dict['rake_percent']) / 100                   # How much to rake when there is a profitable trade made
HEDGE_SYMBOL                   = str(g_cfg_dict['hedge_symbol'])                           # Which coin to place the hedge on
HEDGE_LEVERAGE                 = int(g_cfg_dict['hedge_leverage'])                         # leverage to use when creating a hedge (20x, 50x, 75x, etc.)
HEDGE_PERCENT                  = float(g_cfg_dict['hedge_percent']) / 100                  # fully balanced hedge will be -> short_total=long_total
HEDGE_STOP_PERCENT             = float(g_cfg_dict['hedge_stop_percent']) / 100             # when to close the hedge if it is losing too much money
SHORT_LONG_RATIO_LIMIT_PERCENT = float(g_cfg_dict['short_long_ratio_limit_percent']) / 100 # Places a threshold on when and when not to hedge based on the ratio of short_total/long_total or long_total/short_total
CLOSE_PERCENT                  = float(g_cfg_dict['close_percent']) / 100                  # The +/- pnl threshold to close an open position when margin ratio is above MARGIN_RATIO_THRESHOLD
REOPEN_ORDERS_THRESHOLD        = MARGIN_RATIO_THRESHOLD / 2                                # Reopen all of our closed orders once we drop below this threshold


# trying to set these up above in the same line gives the opposite result when using: TEXT = bool(g_cfg_dict['text'])
if g_cfg_dict['text'] == "True":
    TEXT = True
else:
    TEXT = False

if g_cfg_dict['phone_call'] == "True":
    PHONE_CALL = True
else:
    PHONE_CALL = False

if g_cfg_dict['rake'] == "True":
    RAKE = True
else:
    RAKE = False

if g_cfg_dict['buy_bnb'] == "True":
    BUY_BNB = True
else:
    BUY_BNB = False



# Make sure we are given valid inputs for variables

if MARGIN_RATIO_THRESHOLD < 1:
    MARGIN_RATIO_THRESHOLD = 1
elif MARGIN_RATIO_THRESHOLD > 90:
    MARGIN_RATIO_THRESHOLD = 90


if RAKE_PERCENT*100 < 0:
    RAKE_PERCENT = 0
elif RAKE_PERCENT*100 > 100:
    RAKE_PERCENT = 100


if HEDGE_PERCENT*100 < 0:
    HEDGE_PERCENT = 0
elif HEDGE_PERCENT*100 > 100:
    HEDGE_PERCENT = 100


if HEDGE_LEVERAGE < 1:
    HEDGE_LEVERAGE = 1
elif HEDGE_LEVERAGE > 125:
    HEDGE_LEVERAGE = 125


if HEDGE_STOP_PERCENT*100 > 100:
    HEDGE_STOP_PERCENT = 100
elif HEDGE_STOP_PERCENT*100 < 0:
    HEDGE_STOP_PERCENT = 0


if SHORT_LONG_RATIO_LIMIT_PERCENT*100 < 10:
    SHORT_LONG_RATIO_LIMIT_PERCENT = 10
elif SHORT_LONG_RATIO_LIMIT_PERCENT*100 > 90:
    SHORT_LONG_RATIO_LIMIT_PERCENT = 90


if CLOSE_PERCENT*100 > 100:
    CLOSE_PERCENT = 100
elif CLOSE_PERCENT*100 < 0:
    CLOSE_PERCENT = 0
