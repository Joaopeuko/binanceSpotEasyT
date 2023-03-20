import requests
import numpy as np
import pandas as pd
from abstractEasyT import rates
from supportLibEasyT import log_manager

from binanceSpotEasyT.timeframe import TimeFrame
from binanceSpotEasyT.util import setup_environment


class Rates(rates.Rates):

    def __init__(self,
                 symbol: str,
                 timeframe: TimeFrame,
                 count: int):
        """
        Args:
            symbol:
                The symbol you want to retrieve previous data.

            timeframe:
                The timeframe you want information, like 1 minute, 5 minute, 1 week. You can find all the timeframe
                available in the TimeFrame Class (binanceSpotEasyT.timeframe).

            count:
                It is the amount of information in the past you want. If your time frame is 5 minutes and your count is 4,
                it will return 4 values containing time, open, high, low, close, tick_volume information of this past 4
                candlesticks.
        """

        self._log = log_manager.LogManager('binance-spot')
        self._log.logger.info('Logger Initialized in Initialize')

        self.url_base, self._key, self._secret = setup_environment(self._log)

        self._timeframe = timeframe
        self._symbol = symbol.upper()
        self._count = count

        self.time = None
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.tick_volume = None

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

    def change_timeframe(self, new_timeframe: TimeFrame) -> None:
        """
        This function changes the timeframe.

        Args:
            new_timeframe:
                It receives the new timeframe

        Returns:
            It updates the self._timeframe to the new timeframe.

        """
        self._timeframe = new_timeframe

    def change_count(self, new_count: int) -> None:
        """
        This function changes the count.

        Args:
            new_count:
                It receives the new new_count

        Returns:
            It updates the self._count to the new count.

        Examples:
            >>> # All the code you need to execute the function:
            >>> from binanceSpotEasyT.initialization import Initialize
            >>> from binanceSpotEasyT.timeframe import TimeFrame
            >>> from binanceSpotEasyT.rates import Rates
            >>> initialize = Initialize()
            >>> initialize.initialize_platform()
            >>> initialize.initialize_symbol('BTCUSDT')
            >>> timeframe = TimeFrame()
            >>> # it will get the last 20 one minute candlestick information.
            >>> btcusdt_rates = Rates(symbol='BTCUSDT', timeframe=timeframe.ONE_MINUTE, count=20)
            >>> btcusdt_rates.update_rates()
            >>> len(btcusdt_rates.close)
            20
            >>> # When you change the count, you need to update the information, and you can see that it worked.
            >>> btcusdt_rates.change_count(5)
            >>> btcusdt_rates.update_rates()
            >>> len(btcusdt_rates.close)
            5

            You can ask for this information: time, open, high, low, close, tick_volume.

       """
        self._count = new_count

    def update_rates(self):
        """
                Everytime this function is called it update the last values, it is important to have an updated
                information to calculate indicators and ensure your trading strategy is working properly.

                Returns:
                    It updates the attributes in the constructor.

                Examples:
                    >>> # All the code you need to execute the function:
                    >>> from binanceSpotEasyT.initialization import Initialize
                    >>> from binanceSpotEasyT.timeframe import TimeFrame
                    >>> from binanceSpotEasyT.rates import Rates
                    >>> initialize = Initialize()
                    >>> initialize.initialize_platform()
                    >>> timeframe = TimeFrame()
                    >>> initialize.initialize_symbol('BTCUSDT')
                    >>> # it will get the last 20 one minute candlestick information, but it will return none at the first time.
                    >>> # the rates need the information to be updated everytime.
                    >>> btcusdt_rates = Rates(symbol='BTCUSDT', timeframe=timeframe.ONE_MINUTE, count=20)
                    >>> # The first time, if you try to get a rates information of the close price you will receive None
                    >>> btcusdt_rates.close
                    None
                    >>> # But when you update the rates, the prices will be updated.
                    >>> btcusdt_rates.update_rates()
                    >>> # And the rates will be returned for the information you want.
                    >>> btcusdt_rates.close
                    array([47526.5 , 47501.77, 47507.21, 47481.75, 47476.75, 47494.48,
                           47497.64, 47486.77, 47484.85, 47499.99, 47498.11, 47487.96,
                           47473.43, 47459.  , 47466.4 , 47459.01, 47481.22, 47489.09,
                           47510.48, 47520.  ])

                    You can ask for this information: time, open, high, low, close, tick_volume.

                """
        self._log.logger.info('Rates updated')

        url_rates = '/api/v3/klines'

        payload = {'symbol': self._symbol.upper(),
                   'interval': self._timeframe,
                   'limit': self._count}

        result = pd.DataFrame(requests.get(self.url_base + url_rates, params=payload).json())

        columns = ['Open time',
                   'Open',
                   'High',
                   'Low',
                   'Close',
                   'Volume',
                   'Close time',
                   'Quote asset volume',
                   'Number of trades',
                   'Taker buy base asset volume',
                   'Taker buy quote asset volume',
                   'Ignore']

        result.columns = columns

        self.time = result['Open time']
        self.open = result['Open'].astype(np.float64).values
        self.high = result['High'].astype(np.float64).values
        self.low = result['Low'].astype(np.float64).values
        self.close = result['Close'].astype(np.float64).values
        self.tick_volume = result['Number of trades']
