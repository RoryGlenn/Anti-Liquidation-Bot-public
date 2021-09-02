
class PositionSideType():
    BOTH = "BOTH"

class SideType():
    SIDE_BUY  = 'BUY'
    SIDE_SELL = 'SELL'

class TimeType():
    TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
    TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
    TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill
    TIME_IN_FORCE_GTX = 'GTX'  # Post only order    

class OrderType():
    FUTURE_ORDER_TYPE_LIMIT              = 'LIMIT'
    FUTURE_ORDER_TYPE_MARKET             = 'MARKET'
    FUTURE_ORDER_TYPE_STOP               = 'STOP'
    FUTURE_ORDER_TYPE_STOP_MARKET        = 'STOP_MARKET'
    FUTURE_ORDER_TYPE_TAKE_PROFIT        = 'TAKE_PROFIT'
    FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'
    FUTURE_ORDER_TYPE_LIMIT_MAKER        = 'LIMIT_MAKER'


