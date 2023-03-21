from unittest.mock import patch

import pytest
import requests

from binanceSpotEasyT.initialization import Initialize
from binanceSpotEasyT.initialization import PlatformNotInitialized
from binanceSpotEasyT.initialization import SymbolNotFound
from tests.conftest import MockResponse


class TestInitialization:
    # ------------------------------ Platform ------------------------------ #
    @patch("tests.test_initialization.Initialize", side_effect=PlatformNotInitialized)
    def test_initialize_platform_fail_raises(self, mock):
        with pytest.raises(PlatformNotInitialized):
            Initialize().initialize_platform()

    @patch.object(requests, "get")
    def test_initialize_platform_succeed(self, mock_requests):
        mock_requests.return_value = MockResponse({}, 200)

        result = Initialize().initialize_platform()
        assert result is True

    # ------------------------------ Symbol ------------------------------ #

    @patch.object(requests, "get")
    def test_initialize_symbol_succeed(self, mock_requests):
        mock_requests.return_value = MockResponse({}, 200)

        symbol = "BTCUSDT"

        result = Initialize().initialize_symbol(symbol)
        assert result is True

    @patch.object(requests, "get")
    def test_initialize_symbol_succeed(self, mock_requests):
        mock_requests.return_value = MockResponse({}, 200)

        symbol = "btcusdt"

        result = Initialize().initialize_symbol(symbol)
        assert result is True

    @patch("tests.test_initialization.Initialize", side_effect=SymbolNotFound)
    def test_initialize_symbol_fail(self, mock):
        symbol = "BTC USDT"

        with pytest.raises(SymbolNotFound):
            Initialize().initialize_symbol(symbol)
