"""Configuration details for connecting alpha vantage."""
import datetime
import requests

_API_KEY = None
BASE_URL = 'https://www.alphavantage.co/query'
FUNCTION = 'TIME_SERIES_DAILY'

META_DATA_KEY = 'Meta Data'
LAST_REFRESHED = '3. Last Refreshed'

DATA_KEY = 'Time Series (Daily)'
CLOSE_KEY = '4. close'

DATE_FORMAT = '%Y-%m-%d'


def configure(configuration):
    """Read the alpha vantage key out of the configuration object and store it in the api key global."""
    global _API_KEY
    _API_KEY = configuration.get('alpha_vantage', dict()).get('api_key', None)


def get_price_information(symbol, date=None):
    """
    Accessor for retrieving the price information from alphavantage web service.
    :param symbol: ticker symbol to look up.
    :param date: date to look up content for.  If None, will return the data for the last updated object.
    :return: tuple containing the date and the closing value for the symbol.
    """
    payload = {
        'function': FUNCTION,
        'apikey': _API_KEY,
        'symbol': symbol,
        'datatype': 'json',
        'outputsize': 'compact'
    }

    r = requests.get(BASE_URL, params=payload)

    json_data = r.json()

    if date is None:
        date_key = json_data[META_DATA_KEY][LAST_REFRESHED]
    else:
        date_key = date.strftime(DATE_FORMAT)

    return datetime.datetime.strptime(date_key, DATE_FORMAT).date(), \
           json_data.get(DATA_KEY, {}).get(date_key, {}).get(CLOSE_KEY)
