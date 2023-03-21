import hashlib
import hmac
import time
from urllib.parse import urlencode

import requests
from abstractEasyT import initialization
from supportLibEasyT import log_manager

from binanceSpotEasyT.util import get_account
from binanceSpotEasyT.util import setup_environment


class PlatformNotInitialized(BaseException):
    """Raise this error when ping was not able to be retrieved."""


class SymbolNotFound(BaseException):
    """Raise this error when the symbol is not found."""


class Initialize(initialization.Initialize):
    """
    This class ensure that the platform are working properly.
    If it is connected on the internet, and if the symbol that you are trying to use exists or was not mistyped.
    """

    def __init__(self):
        """
        Initialize the constructor and set the _log.
        """

        self._log = log_manager.LogManager("binance-spot")
        self._log.logger.info("Logger Initialized in Initialize")

        self.symbol_initialized = []

        self.url_base, self._key, self._secret = setup_environment(self._log)

    def _initialize_account(self) -> bool:
        """
        This function check if it is possible to login into Binance using the API KEY and SECRET.
        You must have this information.

        Raises:
            raise_for_status():
                This error happens when it returns an error.

        Returns:
            It returns True if it works fine.

        """

        get_account(self._log, self.url_base, self._key, self._secret)

        return True

    def initialize_platform(self) -> bool:
        """
        This function is responsible to initialize the platform that will be used to trade.

        Raises:
            PlatformNotInitialized:
                Raise this error when there are some problem with internet connection.

        Returns:
            It returns true if initialized else return false.

        Examples:
            >>> # All the code you need to execute the function:
            >>> from binanceSpotEasyT.initialization import Initialize
            >>> initialize = Initialize()
            >>> # The function and the function return:
            >>> initialize.initialize_platform()
            True

        """
        self._log.logger.info("Initializing Binance Spot.")

        url_ping = "/api/v3/ping"
        ping = requests.get(self.url_base + url_ping)
        ping.raise_for_status()

        if ping.json() == {}:
            self._log.logger.info("Ping connection accepted, checking account.")
            self._initialize_account()
            self._log.logger.info("Binance Spot successfully initialized.")
            return True

        else:
            self._log.logger.error("Initialization failed, check internet connection.")

            raise PlatformNotInitialized

    def initialize_symbol(self, *symbols: str) -> bool:
        """
        This function is responsible to initialize as many symbols as you want.

        Args:
            symbols:
                It receives strings as parameters containing the symbol names to be initialized.

        Raises:
            SymbolNotFound: If not possible to initialize the symbol raises this error.

        Returns:
            When the symbol is successfully initialized it returns True and, it updates the list
            self.symbol_initialized if you want to work with the symbols correctly initialized.

        Examples:
            >>> # All the code you need to execute the function:
            >>> from binanceSpotEasyT.initialization import Initialize
            >>> initialize = Initialize()
            >>> initialize.initialize_platform()
            True
            >>> # The function and the function return:
            >>> initialize.initialize_symbol('BTCUSDT')
            True
            >>> # Check initialize.symbol_initialized to see the list of initialized symbols
            >>> initialize.symbol_initialized
            ['BTCUSDT']

        """
        self._log.logger.info("Initializing symbols.")

        url_exchange_info = "/api/v3/exchangeInfo"

        for symbol in symbols:
            symbol = symbol.upper()
            self._log.logger.info(f"Initializing {symbol}.")
            payload = {"symbol": symbol}

            exchange_info = requests.get(self.url_base + url_exchange_info, params=payload)

            # Prepare the symbol to open positions
            if exchange_info.status_code != 200:
                self._log.logger.error(f"It was not possible to initialize {symbol}, symbol not found or not visible.")
                raise SymbolNotFound

            else:
                self.symbol_initialized.append(symbol)
                self._log.logger.info(f"{symbol} successfully initialized.")

        return True
