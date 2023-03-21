import hashlib
import hmac
import math
import time
from urllib.parse import urlencode

import numpy as np
import requests
from abstractEasyT import trade
from supportLibEasyT import log_manager

from binanceSpotEasyT.util import get_price_last
from binanceSpotEasyT.util import get_symbol_asset_balance
from binanceSpotEasyT.util import setup_environment


class Trade(trade.Trade):
    """
    This class is responsible to handle all the trade requests.
    """

    def __init__(self, symbol: str, lot: float, stop_loss: float, take_profit: float):
        """
        It is allowed to have only one position at time per symbol, right now it is not possible to open a position and
        increase the size of it or to open opposite position. Open an open position will close the other direction one.

        Args:
            symbol:
                It is the symbol you want to open or close or check if already have an operation opened.

            lot:
                It is how many shares you want to trade, many symbols allow fractions and others requires a
                certain amount. It can be 0.01, 100.0, 1000.0, 10000.0.

            stop_loss:
                It is how much you accept to lose. Example: If you buy a share for US$10.00, and you accept to lose US$1.00
                you set this variable at 1.00, you will be out of the operation at US$9.00 (sometimes more, somtime less,
                the US$9.00 is the trigger). Keep in mind that some symbols has different points metrics, US$1.00 sometimes
                can be 1000 points.

            take_profit:
                It is how much you accept to win. Example: If you buy a share for US$10.00, and you accept to win US$1.00
                you set this variable at 1.00, you will be out of the operation at US$11.00 (sometimes more, somtime less,
                the US$11.00 is the trigger). Keep in mind that some symbols has different points metrics, US$1.00 sometimes
                can be 1000 points.

        """

        self._log = log_manager.LogManager("binance-spot")
        self._log.logger.info("Logger Initialized in Trade")

        self.symbol = symbol.upper()
        self.lot = lot
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        self.points = 8

        self.url_base, self._key, self._secret = setup_environment(self._log)

        self._trade_allowed = False

        self.trade_direction = None  # 'buy', 'sell', or None for no position
        self.position_check()

    def normalize(self, price: float) -> float:
        """
        This function normalize the price to ensure a precision that is required by the platform

        Args:
            price:
                It is the price that you want to be normalized, usually is the last price to open a market position.

        Returns:
            It returns the float price normalized under a precision that is accepted by the platform.

        Examples:

            >>> # All the code you need to execute the function:
            >>> from binanceSpotEasyT.initialization import Initialize
            >>> from binanceSpotEasyT.trade import Trade
            >>> initialize = Initialize()
            >>> initialize.initialize_platform()
            >>> initialize.initialize_symbol('BTCUSDT')
            >>> btcusdt_trade = Trade(symbol='BTCUSDT', lot=1.0, stop_loss=1.0, take_profit=1.0)
            >>> # The normalize function is used inside other functions, but the idea is to normalize the value to
            >>> # be accepted in the trade request. If you want to see this function in action you can look at
            >>> # open_buy() and open_sell()
            >>> btcusdt_trade.normalize(12.3456789101112131415)
            12.3456789

        """
        self._log.logger.info("Normalizing the price")
        return np.round_(price, self.points)

    def open_buy(self):
        """
        This functions when called send a buy request to Binance with the parameters in the attributes.

        Returns:
            It returns None, but if an error occurs when open a position it will break.

        Examples:

            Try this on your demo account with fake money, a position will be opened.

            >>> # All the code you need to execute the function:
            >>> from binanceSpotEasyT.initialization import Initialize
            >>> from binanceSpotEasyT.trade import Trade
            >>> initialize = Initialize()
            >>> initialize.initialize_platform()
            True
            >>> initialize.initialize_symbol('BTCUSDT')
            >>> # Notice that the stop and profit are zero, that is because the Spot do not use it.
            >>> btcusdt_trade = Trade(symbol='BTCUSDT', lot=0.01, stop_loss=0.0, take_profit=0.0)
            >>> # When it works it returns None
            >>> btcusdt_trade.open_buy()
            None
            >>> # Just for curiosity, if you want to try to open a buy position with this sell opened you will close
            >>> # the sell position
            >>> btcusdt_trade.open_sell()
            None

        """

        price_last = get_price_last(self.url_base, self.symbol)

        self._log.logger.info(f"BUY Order sent: {self.symbol}," f" {self.lot} lot(s)," f" at {price_last}")

        url_order = "/api/v3/order"

        time_stamp = int(time.time() * 1000)
        payload = {
            "symbol": self.symbol,
            "side": "BUY",
            "type": "MARKET",
            "quantity": self.lot,
            "recvWindow": 5000,
            "timestamp": time_stamp,
        }

        payload_encoded = urlencode(payload)
        signature = hmac.new(
            self._secret.encode("utf-8"),
            payload_encoded.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        payload["signature"] = signature
        order = requests.post(
            self.url_base + url_order,
            params=payload,
            headers={
                "X-MBX-APIKEY": self._key,
            },
        )

        order.raise_for_status()

        self._log.logger.info("Change trade direction to BUY.")
        self.trade_direction = "buy"

    def open_sell(self):
        """
        This functions when called send a sell request to Binance with the parameters in the attributes.

        Returns:
            It returns None, but if an error occurs when open a position it will break.

        Examples:

            Try this on your demo account with fake money, a position will be opened.

            >>> # All the code you need to execute the function:
            >>> from binanceSpotEasyT.initialization import Initialize
            >>> from binanceSpotEasyT.trade import Trade
            >>> initialize = Initialize()
            >>> initialize.initialize_platform()
            True
            >>> initialize.initialize_symbol('BTCUSDT')
            >>> # Notice that the stop and profit are zero, that is because the Spot do not use it.
            >>> btcusdt_trade = Trade(symbol='BTCUSDT', lot=0.01, stop_loss=0.0, take_profit=0.0)
            >>> # When it works it returns None
            >>> btcusdt_trade.open_sell()
            None
            >>> # Just for curiosity, if you want to try to open a buy position with this sell opened you will close
            >>> # the sell position
            >>> btcusdt_trade.open_buy()
            None

        """

        price_last = get_price_last(self.url_base, self.symbol)

        self._log.logger.info(f"SELL Order sent: {self.symbol}," f" {self.lot} lot(s)," f" at {price_last}")

        url_order = "/api/v3/order"

        time_stamp = int(time.time() * 1000)
        payload = {
            "symbol": self.symbol,
            "side": "SELL",
            "type": "MARKET",
            "quantity": self.lot,
            "recvWindow": 5000,
            "timestamp": time_stamp,
        }

        payload_encoded = urlencode(payload)
        signature = hmac.new(
            self._secret.encode("utf-8"),
            payload_encoded.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        payload["signature"] = signature
        order = requests.post(
            self.url_base + url_order,
            params=payload,
            headers={
                "X-MBX-APIKEY": self._key,
            },
        )

        order.raise_for_status()

        self._log.logger.info("Change trade direction to SELL.")
        self.trade_direction = "sell"

    def position_open(self, buy: bool, sell: bool) -> str or None:
        """
        This function receives two bool variables, buy and sell, if one of this variable is true and the other is false,
        it opens a position to the side that is true, if both variable is true or both variable is false, it does not
        open a position.

        Args:
            buy:
                When buy is TRUE it receives a positive signal to open a position. When false, it is ignored.

            sell:
                When sell is TRUE it receives a positive signal to open a position. When false, it is ignored.

        Returns:
            It opens the position.

        Examples:

            Try this on your demo account with fake money, a position will be opened.

            >>> # All the code you need to execute the function:
            >>> from binanceSpotEasyT.initialization import Initialize
            >>> from binanceSpotEasyT.trade import Trade
            >>> initialize = Initialize()
            >>> initialize.initialize_platform()
            True
            >>> initialize.initialize_symbol('BTCUSDT')
            True
            >>> # Notice that the stop and profit are zero, that is because the Spot do not use it.
            >>> btcusdt_trade = Trade(symbol='BTCUSDT', lot=0.01, stop_loss=0.0, take_profit=0.0)
            >>> # _trade_allowed is False by default, this attribute will be handled in another project,
            >>> # that is why it exists. Let assign to True and see what happens:
            >>> btcusdt_trade._trade_allowed = True
            >>> btcusdt_trade._trade_allowed
            True
            >>> # Currently, I do not have a position for BTC, so first I will try to open a SELL position to see
            >>> # what happens since it is not allowed.
            >>> btcusdt_trade.position_open(False, True)
            2022-03-29 10:36:38,580 WARNING - warning - A SELL position are not allowed in Binance Spot, you can only sell a symbol if you have it.
            2022-03-29 10:36:38,580 WARNING - warning - A SELL position are not allowed in Binance Spot, you can only sell a symbol if you have it.
            # Now that you know what happens lets try to BUY a position.
            >>> btcusdt_trade.position_open(True, False)
            'buy'
            >>> # It worked as a expected, let close it. You can check, the position will be closed.
            >>> btcusdt_trade.position_close()
            None
            >>> # To finish, let see what happens if both arguments are True
            >>> btcusdt_trade.position_open(True, True)
            None
            >>> # Nothing happens, but when both are False?
            >>> btcusdt_trade.position_open(False, False)
            None
            >>> # Nothing happens

        """

        self._log.logger.info(
            f"Open position called. BUY is {str(buy)}, and SELL is {str(sell)}. Trade allowed is "
            f"{self._trade_allowed}."
        )

        if self._trade_allowed and self.trade_direction is None:
            if buy and not sell:
                self.open_buy()
                self.position_check()

            if sell and not buy:
                self._log.warning(
                    "A SELL position are not allowed in Binance Spot, you can only sell a symbol" " if you have it."
                )
                self.position_check()

        return self.trade_direction

    def position_close(self) -> None:
        """
        This functions checks the trade direction, and it opens an opposite position to the current one to close it.
        If there is no position nothing happens.

        Returns:
            Close the current position by opening an opposite one.

        Examples:

            Try this on your demo account with fake money, a position will be opened.

            >>> # All the code you need to execute the function:
            >>> from binanceSpotEasyT.initialization import Initialize
            >>> from binanceSpotEasyT.trade import Trade
            >>> initialize = Initialize()
            >>> initialize.initialize_platform()
            True
            >>> initialize.initialize_symbol('BTCUSDT')
            >>> btcusdt_trade = Trade(symbol='BTCUSDT', lot=0.01, stop_loss=0.0, take_profit=0.0)
            >>> btcusdt_trade._trade_allowed = True
            >>> # To know more about btcusdt_trade._trade_allowed look the Examples in position_open() documentation.
            >>> btcusdt_trade.position_open(True, Sell)
            'buy'
            >>> # When there is a position opened, btcusdt_trade.position_close() will open a position in a different
            >>> # direction to close it.
            >>> btcusdt_trade.position_close()
            None
            # It checks the trading direction, return none when there is no trade opened.
            >>> btcusdt_trade.trade_direction
            None
            # I will open a buy position, check the trade direction and close it!
            >>> btcusdt_trade.position_open(True, False)
            'buy'
            >>>  btcusdt_trade.trade_direction
            'buy'
            >>> btcusdt_trade.position_close()
            >>> # We can see that it worked!
            >>> # What happens when I call btcusdt_trade.position_close() with no position opened?
            >>> btcusdt_trade.position_close()
            None
            >>> # Nothing happens, there are no position to be closed.

        """
        self._log.logger.info("Close position called.")
        self.position_check()
        if self.trade_direction == "buy":
            self.open_sell()
            self.position_check()

        elif self.trade_direction == "sell":
            self.open_buy()
            self.position_check()

    def position_check(self) -> None:
        """
        This function checks if there are a position opened and update the variable self.trade_direction.
        If there is no position, the self.trade_direction will be updated to None, else, it updates with the trade
        direction, which can be 'sell' or 'buy'.

        Returns:
            This function update the variable self.trade_direction and do not return a result.

        Examples:

            Try this on your demo account with fake money, a position will be opened.

            >>> # All the code you need to execute the function:
            >>> from binanceSpotEasyT.initialization import Initialize
            >>> from binanceSpotEasyT.trade import Trade
            >>> initialize = Initialize()
            >>> initialize.initialize_platform()
            True
            >>> initialize.initialize_symbol('BTCUSDT')
            >>> btcusdt_trade = Trade(symbol='BTCUSDT', lot=0.01, stop_loss=0.0, take_profit=0.0)
            >>> btcusdt_trade._trade_allowed = True
            >>> # Position check it is just to ensure that the btcusdt_trade.trade_direction are in the right direction.
            >>> # The btcusdt_trade.trade_direction is automatically handled by buy open_sell() and open_buy() and
            >>> # it returns the trade direction or None when there is no trade opened.
            >>> btcusdt_trade.trade_direction
            None
            >>> btcusdt_trade.position_open(True, False)
            'buy'
            >>> btcusdt_trade.trade_direction
            'buy'
            >>> # After I open a buy position, it returns 'buy' to trade_direction, but, what happens if I manually
            >>> # change the direction?
            >>> btcusdt_trade.trade_direction = 'coffee shop'
            >>> btcusdt_trade.trade_direction
            'coffee shop'
            >>> # It is possible to see that the trade_direction was changed.
            >>> # and the position_check() is called in all the functions that opens and closes position
            >>> # to ensure that direction is correct, I will call position_check() to fix my change to 'coffee shop'
            >>> btcusdt_trade.position_check()
            None
            >>> btcusdt_trade.trade_direction
            'buy'
            >>> # It worked.
            >>> # That is it, I will just the position that I opened before.
            >>> btcusdt_trade.position_close()

        """
        self._log.logger.info("Calls Binance-Spot to check if there is a position opened.")

        balance_asset = get_symbol_asset_balance(self._log, self.url_base, self._key, self._secret, self.symbol)

        if float(balance_asset) != 0.00000000:
            self.trade_direction = "buy"

        else:
            self.trade_direction = None
