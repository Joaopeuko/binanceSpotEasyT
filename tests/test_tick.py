import requests
import datetime
from unittest.mock import patch
from binanceSpotEasyT.tick import Tick


class TestTick:

    def test_tick_created_but_not_updated(self):
        symbol = 'EURUSD'

        tick = Tick(symbol=symbol)

        assert tick.time is None
        assert tick.bid is None
        assert tick.ask is None
        assert tick.last is None
        assert tick.volume is None

    @patch.object(requests, 'get')
    def test_type(self, mock_tick):
        mock_tick.return_value.time = datetime.datetime(year=2022, month=1, day=1)
        mock_tick.return_value.bid = 1.0
        mock_tick.return_value.ask = 1.0
        mock_tick.return_value.last = 1.0
        mock_tick.return_value.volume = 1.0

        symbol = 'BTCUSDT'

        tick = Tick(symbol=symbol)

        tick.get_new_tick()

        assert type(tick.time) == datetime.datetime
        assert type(tick.bid) == float
        assert type(tick.ask) == float
        assert type(tick.last) == float
        assert type(tick.volume) == float
