"""
Configuration and service associated with calculating the asset allocation for a given stock ticker symbol.
"""
from decimal import Decimal

investment_allocations = dict()


def configure(definition):
    global investment_allocations
    data = definition['investment_allocations']

    decimal_100 = Decimal('100.0')

    for allocation_definition in data:
        breakdown = {key: (Decimal(value) / decimal_100) for key, value in allocation_definition['breakdown'].iteritems()}
        investment_allocations[allocation_definition['symbol']] = breakdown


def get_asset_allocation(ticker, amount):

    allocation_data = investment_allocations.get(ticker, None)
    result = dict()

    if allocation_data is None:
        print "Couldn't find data for ticker: %s" % ticker
        allocation_data = dict(other=Decimal(1.0))

    for key, percentage in allocation_data.iteritems():
        result[key] = amount * percentage
    return result
