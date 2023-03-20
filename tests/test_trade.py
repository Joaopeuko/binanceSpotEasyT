import requests

import binanceSpotEasyT
from unittest.mock import patch
from binanceSpotEasyT.trade import Trade


class TestTrade:

    def test_normalize(self):
        symbol = 'BTCUSDT'
        lot = 0.01
        stop_loss = 0.0
        take_profit = 0.0

        trade = Trade(symbol=symbol,
                      lot=lot,
                      stop_loss=stop_loss,
                      take_profit=take_profit)

        value_to_normalize = 12.3456789101112131415
        result = trade.normalize(value_to_normalize)
        assert result == 12.34567891

    @patch.object(requests, 'post')
    def test_open_buy(self, mock_request):
        symbol = 'BTCUSDT'
        lot = 0.01
        stop_loss = 0.0
        take_profit = 0.0

        trade = Trade(symbol=symbol,
                      lot=lot,
                      stop_loss=stop_loss,
                      take_profit=take_profit)

        trade.position_check()
        assert trade.trade_direction is None
        trade.open_buy()
        assert trade.trade_direction is 'buy'

    @patch.object(requests, 'post')
    def test_open_sell(self, mock_request):
        symbol = 'BTCUSDT'
        lot = 0.01
        stop_loss = 0.0
        take_profit = 0.0

        trade = Trade(symbol=symbol,
                      lot=lot,
                      stop_loss=stop_loss,
                      take_profit=take_profit)

        trade.trade_direction = 'buy'  # it because in spot it cannot have a sell position. It close opens position only

        assert trade.trade_direction is 'buy'
        trade.open_sell()
        assert trade.trade_direction is 'sell'
    #

    @patch.object(Trade, 'position_open')
    @patch.object(requests, 'post')
    def test_position_open(self, mock_request, mock_position_open):

        symbol = 'BTCUSDT'
        lot = 0.01
        stop_loss = 0.0
        take_profit = 0.0

        trade = Trade(symbol=symbol,
                      lot=lot,
                      stop_loss=stop_loss,
                      take_profit=take_profit)

        trade._trade_allowed = True

        mock_position_open.return_value = 'buy'
        result = trade.position_open(buy=True, sell=False)
        assert result is 'buy'

        mock_position_open.return_value = 'sell'
        result = trade.position_open(False, True)
        assert result is 'sell'

        mock_position_open.return_value = None
        result = trade.position_open(False, False)
        assert result is None

        mock_position_open.return_value = None
        result = trade.position_open(True, True)
        assert result is None

    @patch.object(Trade, 'position_open')
    @patch.object(requests, 'post')
    def test_position_close(self, mock_request, mock_position_open):

        symbol = 'BTCUSDT'
        lot = 0.01
        stop_loss = 0.0
        take_profit = 0.0

        trade = Trade(symbol=symbol,
                      lot=lot,
                      stop_loss=stop_loss,
                      take_profit=take_profit)

        trade._trade_allowed = True

        mock_position_open.return_value = 'buy'
        result = trade.position_open(buy=True, sell=False)
        assert result is 'buy'

        # mock_position_close.return_value = None
        trade.position_close()
        assert trade.trade_direction is None

    @patch.object(requests, 'get')
    def test_trade_allowed_direction_none(self, mock_request):

        symbol = 'BTCUSDT'
        lot = 0.01
        stop_loss = 0.0
        take_profit = 0.0

        trade = Trade(symbol=symbol,
                      lot=lot,
                      stop_loss=stop_loss,
                      take_profit=take_profit)

        trade._trade_allowed = True

        assert trade.trade_direction is None
        assert trade._trade_allowed is True

    @patch('binanceSpotEasyT.trade.get_symbol_asset_balance')
    def test_position_check(self, mock_balance):

        symbol = 'BTCUSDT'
        lot = 0.01
        stop_loss = 0.0
        take_profit = 0.0

        trade = Trade(symbol=symbol,
                      lot=lot,
                      stop_loss=stop_loss,
                      take_profit=take_profit)

        trade._trade_allowed = True

        mock_balance.return_value = 0.01
        trade.position_check()
        assert trade.trade_direction is 'buy'



