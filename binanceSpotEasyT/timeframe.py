from abstractEasyT import timeframe


class TimeFrame(timeframe.TimeFrame):
    """
    There are incompatibilities and different patterns in writing the timeframe between platforms.
    This class attend to reduce the chance of errors providing the same timeframe structure between platforms.

    Examples:
        You can find an example of the TimeFrame usage in update_rates() function in Rates documentation
    """

    def __init__(self):

        self.ONE_MINUTE = '1m'  # 1 minute
        self.TWO_MINUTES = None  # 2 minutes
        self.THREE_MINUTES = '3m'  # 3 minutes
        self.FOUR_MINUTES = None  # 4 minutes
        self.FIVE_MINUTES = '5m'  # 5 minutes
        self.SIX_MINUTES = None  # 6 minutes
        self.TEN_MINUTES = None  # 10 minutes
        self.TWELVE_MINUTES = None  # 12 minutes
        self.FIFTEEN_MINUTES = '15m'  # 15 minutes
        self.TWENTY_MINUTES = None  # 20 minutes
        self.THIRTY_MINUTES = '30m'  # 30 minutes
        self.ONE_HOUR = '1h'  # 1 hour
        self.TWO_HOURS = '2h'  # 2 hour
        self.THREE_HOURS = None  # 3 hour
        self.FOUR_HOURS = '4h '  # 4 hour
        self.SIX_HOURS = '6h'  # 6 hour
        self.EIGHT_HOURS = '8h'  # 8 hour
        self.TWELVE_HOURS = '12h'  # 12 hour
        self.ONE_DAY = '1d'  # 1 Day
        self.THREE_DAY = '3d'  # 3 Days
        self.ONE_WEEK = '1w'  # 1 Week
        self.ONE_MONTH = '1M'  # 1 Month
