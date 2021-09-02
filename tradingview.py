from tradingview_ta import TA_Handler, Interval


def get_symbols_from_file():
    symbol_list = list()
    with open("binance_futures_symbols.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            symbol_list.append(line.strip("\n"))
    return symbol_list



def get_analysis(symbol_list):
    for symbol in symbol_list:
        try:
            futures = TA_Handler(
                symbol=symbol,
                screener="crypto",
                exchange="binance",
                interval=Interval.INTERVAL_4_HOURS
            )

            recommendation = futures.get_analysis().summary['RECOMMENDATION']

            if recommendation == 'BUY' or recommendation == "STRONG_BUY":
                print(symbol, futures.interval, futures.get_analysis().summary)
            if recommendation == 'STRONG_SELL':
                print(symbol, futures.interval, futures.get_analysis().summary)
        except Exception as e:
            print(symbol, e)


if __name__ == '__main__':
    symbols = get_symbols_from_file()
    get_analysis(symbols)

