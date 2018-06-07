"""
Configuration and service associated with calculating the asset allocation for a given stock ticker symbol.
"""
from decimal import Decimal

investment_allocations = {}


def configure(configuration):
    """
    Configure the data dictionary that contains a stock ticker key and the breakdown of stocks, foreign stocks,
    cash, bonds based on percentages.
    """
    global investment_allocations
    data = configuration['investment_allocations']

    decimal_100 = Decimal('100.0')

    for allocation_definition in data:
        breakdown = {key: (Decimal(value) / decimal_100)
                     for key, value in allocation_definition['breakdown'].items()}
        investment_allocations[allocation_definition['symbol']] = breakdown


def get_asset_allocation(ticker, amount):
    """
    Retrieve the asset allocation for the ticker value provided.

    :param ticker: string ticker symbol to look up in the investment allocation.
    :param amount: decimal amount that will be used to calculate cash values for all of the breakdowns in the investment
    allocation.
    :return dictionary containing the breakdown types and the decimal amounts for each breakdown.
    """
    allocation_data = investment_allocations.get(ticker, None)
    result = dict()

    if allocation_data is None:
        print(f"Couldn't find data for ticker: {ticker}") % ticker
        allocation_data = dict(other=Decimal(1.0))

    for key, percentage in allocation_data.items():
        result[key] = amount * percentage
    return result
