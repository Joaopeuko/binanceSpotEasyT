from unittest.mock import patch

import requests

from binanceSpotEasyT.rates import Rates
from binanceSpotEasyT.timeframe import TimeFrame
from tests.conftest import MockResponse


class TestRates:
    def test_rates_created_but_not_updated(self):
        symbol = 'EURUSD'
        count = 20
        timeframe = TimeFrame()

        rates = Rates(symbol=symbol,
                      timeframe=timeframe.ONE_MINUTE,
                      count=count)

        assert rates.time is None
        assert rates.open is None
        assert rates.high is None
        assert rates.low is None
        assert rates.close is None
        assert rates.tick_volume is None

    @patch.object(requests, 'get')
    def test_length(self, mock_requests):
        json_data = {'Open time': range(20),
                     'Open': range(20),
                     'High': range(20),
                     'Low': range(20),
                     'Close': range(20),
                     'Volume': '',
                     'Close time': '',
                     'Quote asset volume': '',
                     'Number of trades': 3,
                     'Taker buy base asset volume': '',
                     'Taker buy quote asset volume': '',
                     'Ignore': ''}

        mock_requests.return_value = MockResponse(json_data, 200)

        symbol = 'BTCUSDT'
        count = 20
        timeframe = TimeFrame()

        rates = Rates(symbol=symbol,
                      timeframe=timeframe.ONE_MINUTE,
                      count=count)

        rates.update_rates()

        assert len(rates.time) == 20
        assert len(rates.open) == 20
        assert len(rates.high) == 20
        assert len(rates.low) == 20
        assert len(rates.close) == 20
        assert len(rates.tick_volume) == 20
