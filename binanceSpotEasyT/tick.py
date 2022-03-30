import datetime

import requests
from abstractEasyT import tick
from supportLibEasyT import log_manager

from binanceSpotEasyT.util import setup_environment


class Tick(tick.Tick):
    """
    Tick class is the responsible to retrieve every tick information.
    """
    def __init__(self,
                 symbol: str):
        """
         Args:
             symbol:
                 It is the symbol you want information about. You can have information about time, bid, ask, last, volume.
         """

        self._log = log_manager.LogManager('binance-spot')
        self._log.logger.info('Logger Initialized in Tick')

        self.url_base, self._key, self._secret = setup_environment(self._log)

        self._symbol = symbol

        self.time = None
        self.bid = None
        self.ask = None
        self.last = None
        self.volume = None

    def change_symbol(self, new_symbol: str) -> None:
        """
        This function changes the symbol.

        Args:
            new_symbol:
                It receives the new symbol

        Returns:
            It updates the self._symbol to the new symbol.

        """
        self._symbol = new_symbol.upper()

    def get_new_tick(self):
        """
                Everytime this function is called it update the last tick information, it is important to have update
                information know the most recent information.

                Returns:
                     It updates the attributes in the constructor.

                Examples:
                    >>> # All the code you need to execute the function:
                    >>> from binanceSpotEasyT.initialization import Initialize
                    >>> from binanceSpotEasyT.tick import Tick
                    >>> initialize = Initialize()
                    >>> initialize.initialize_platform()
                    >>> initialize.initialize_symbol('BTCUSDT')
                    >>> # It will return the most recent information, but it will return None at the first time.
                    >>> # The tick need the information to be updated everytime.
                    >>> btcusdt_tick = Tick(symbol='BTCUSDT')
                    >>> btcusdt_tick.ask
                    None
                    >>> # When you update the tick:
                    >>> btcusdt_tick.get_new_tick()
                    >>> btcusdt_tick.ask
                    1.09975
                    >>> btcusdt_tick.bid
                    1.09975
                    >>> # You must have notice that I used bid and ask, some exchanges do not return the last value
                    >>> # You can find only the information for bid and ask. If you try to return last it will print 0.0.
                    >>> # But remember, not all the exchanges do that, you must check it. Binance return the last value.
                    >>> btcusdt_tick.last
                    47572.46

                    You can ask for this information: time, bid, ask, last, volume.

                """
        self._log.logger.info('Tick updated')

        url_ticker = '/api/v3/ticker/24hr'

        result = requests.get(self.url_base + url_ticker, {'symbol': self._symbol})
        result.raise_for_status()

        ticker = result.json()

        self.time = datetime.datetime.fromtimestamp(ticker['closeTime'] / 1000)
        self.bid = float(ticker['bidPrice'])
        self.ask = float(ticker['askPrice'])
        self.last = float(ticker['lastPrice'])
        self.volume = float(ticker['volume'])
