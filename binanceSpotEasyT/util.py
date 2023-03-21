import hashlib
import hmac
import os
import time
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from supportLibEasyT.log_manager import LogManager


class CredentialsNotFound(BaseException):
    """Raise this error when the key or the BINANCE_API_SECRET are not found, it does not prevent if the key or the BINANCE_API_SECRET are wrong."""


def setup_environment(log) -> (str, str, str):
    """
    This function are responsible to check if the credentials are available, it is used to prevent future problems.

    Args:
        log:
            Receives the log handler to handle this support function.

    Raises:
        CredentialsNotFound:
            This error returns when the key is missing, empty or invalid.

    Returns:

    """
    log.info("Setting up the environment.")

    load_dotenv()
    log.info("Retrieving the base URL")
    url_base = os.environ.get("BINANCE_BASE_URL")
    log.info(f"URL retrieved: {url_base}")

    key = os.environ.get("BINANCE_API_KEY")
    secret = os.environ.get("BINANCE_SECRET_KEY")

    if key is None or secret is None:
        log.error("Your Binance Key or Secret are empty. You must have these information.")
        raise CredentialsNotFound

    elif key == "<insert your credential here>" or secret == "<insert your credential here>":
        log.error("Your Binance Key or Secret was not provided. You must have these information.")
        raise CredentialsNotFound

    return url_base, key, secret


def get_price_last(url_base: str, symbol: str) -> str:
    """
    This function is used to get the last price of a determined symbol, the last price is the most recent one.
    Args:
        url_base:
            url_base is the parameter containing the principal URL to call the endpoint.
            There are many kind of url_base, usually one for test and the other for real transaction.
        symbol:
            The symbol you want the most recent price.

    Returns:
        It returns the price in a string format

    """
    url_price_last = "/api/v3/ticker/price"
    price_last = requests.get(url_base + url_price_last, params={"symbol": symbol})
    price_last.raise_for_status()

    return price_last.json()["price"]


def get_account(log: LogManager, url_base: str, key: str, secret: str) -> dict:
    """
    This functions returns User's account information.
    Args:
        log:
            The log receives a log handler to be able to log the information

        url_base:
            url_base is the parameter containing the principal URL to call the endpoint.
            There are many kind of url_base, usually one for test and the other for real transaction.

        key:
            It is the key used to authenticate transaction for Binance

        secret:
            It is the secret used to authenticate transaction for Binance

    Returns:
        The return is a JSON object that contains account information

    """

    log.info("Get account information from Binance Spot")

    time_stamp = int(time.time() * 1000)
    payload = urlencode(
        {
            "timestamp": time_stamp,
        }
    )

    signature = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

    account = requests.get(
        url_base + "/api/v3/account",
        params={
            "timestamp": time_stamp,
            "signature": signature,
        },
        headers={
            "X-MBX-APIKEY": key,
        },
    )

    account.raise_for_status()

    return account.json()


def get_symbol_asset_balance(log: LogManager, url_base: str, key: str, secret: str, symbol: str) -> float:
    """

    Args:
        log:
            The log receives a log handler to be able to log the information

        url_base:
            url_base is the parameter containing the principal URL to call the endpoint.
            There are many kind of url_base, usually one for test and the other for real transaction.

        key:
            It is the key used to authenticate transaction for Binance

        secret:
            It is the secret used to authenticate transaction for Binance

        symbol:
            The symbol you want to know how much of that currency you have.

    Returns:
        A float number with the amount of a specific currency asked for

    """
    log.info(f"Get the asset balance for {symbol} Binance Spot")
    account = get_account(log, url_base, key, secret)
    balances = pd.DataFrame(account["balances"])
    mask_balance = balances["asset"].values == symbol[:3]

    return balances[mask_balance]["free"].astype(np.float64).item()
