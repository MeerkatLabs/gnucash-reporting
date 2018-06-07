"""
Calculator that will go through and calculate the net worth of the accounts.
"""
import time
from calendar import monthrange
from datetime import date
from decimal import Decimal

from dateutils import relativedelta

from gnucash_reports.collate.bucket import PeriodCollate
from gnucash_reports.collate.bucket_generation import decimal_generator
from gnucash_reports.collate.store import split_summation
from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.configuration.inflation import get_monthly_inflation
from gnucash_reports.periods import PeriodStart, PeriodEnd, PeriodSize
from gnucash_reports.utilities import time_series_dict_to_list
from gnucash_reports.wrapper import account_walker, get_balance_on_date, parse_walker_parameters


def net_worth(assets=None, liabilities=None, start=PeriodStart.this_month_year_ago,
              end=PeriodEnd.today, period_size=PeriodSize.month):
    """
    Create a graph that will calculate the assets, liabilities and net asset changes in values over time.
    :param assets: account walker parameters for the accounts containing assets
    :param liabilities: account walker parameters for the accounts containing liabilities
    :param start: the start of the period for collecting the data
    :param end: the end of the period for collecting data
    :param period_size: the size of the steps between start and end
    :return: dictionary containing:
    assets - time value data containing date and value keys
    liabilities - time value data containing date and liability keys
    net - time value data containing date and net keys
    inflation - time value data containing the inflation increase based on the net value at the start of the period
    """
    assets = assets or []
    liabilities = liabilities or []

    assets = parse_walker_parameters(assets)
    liabilities = parse_walker_parameters(liabilities)

    period_start = PeriodStart(start)
    period_end = PeriodEnd(end)
    period_size = PeriodSize(period_size)

    start_of_trend = period_start.date
    end_of_trend = period_end.date

    asset_bucket = PeriodCollate(start_of_trend, end_of_trend, decimal_generator, split_summation,
                                 frequency=period_size.frequency, interval=period_size.interval)
    liability_bucket = PeriodCollate(start_of_trend, end_of_trend, decimal_generator, split_summation,
                                     frequency=period_size.frequency, interval=period_size.interval)
    net_bucket = PeriodCollate(start_of_trend, end_of_trend, decimal_generator, split_summation,
                               frequency=period_size.frequency, interval=period_size.interval)

    currency = get_currency()

    # Calculate the asset balances
    for account in account_walker(**assets):
        for key, value in asset_bucket.container.items():
            balance = get_balance_on_date(account, key, currency)
            asset_bucket.container[key] += balance

    # Calculate the liability balances
    for account in account_walker(**liabilities):
        for key, value in liability_bucket.container.items():
            balance = get_balance_on_date(account, key, currency)
            liability_bucket.container[key] += balance

    # Now calculate the net values from the difference.
    for key, value in liability_bucket.container.items():
        net_bucket.container[key] = asset_bucket.container[key] + liability_bucket.container[key]

    assets = time_series_dict_to_list(asset_bucket.container)
    # Convert the liabilities to positive values to show the amount of liabilities
    liabilities = time_series_dict_to_list(liability_bucket.container, value=lambda s: -s)
    net = time_series_dict_to_list(net_bucket.container)

    inflation = get_monthly_inflation()
    starting_point = None
    inflation_data = []
    for record in net:
        if starting_point:
            starting_point += (starting_point * inflation)
        else:
            starting_point = record[1]

        inflation_data.append((record[0], starting_point))

    inflation = inflation_data

    return {'assets': assets, 'liabilities': liabilities, 'net': net, 'inflation': inflation}


def net_worth_table(assets=None, liabilities=None, trends=None, deltas=None):
    """
    Generate a report that will show simple trends based on previous months, as well as calculating the deltas.
    :param assets: account walker parameters with additional field 'name'
    :param liabilities: account walker parameters with additional field 'name'
    :param trends: the months to show values for
    :param deltas: the months to show the change in values for
    :return: dictionary containing
    trend - list of time objects for each of the trend values (header)
    deltas - list of the delta values (header)
    assets - dictionary containing
      records - the list of sub accounts stored in the report containing
        name - the name of the record
        current_data - the current value in the account
        deltas - a list of the value in the account for the deltas
        trend - a list of the value in the account for the trend query
      current_data - the current value of all the records
      deltas - the list of the deltas for all the records
      trend - the list of the trends for all the records
    liability - dictionary containing the same breakdown as the assets
    net_worth - dictionary containing the same breakdown as the assets
    """
    asset_definitions = assets or []
    liability_definitions = liabilities or []
    trends = trends or [-2, -1]
    deltas = deltas or [-1, -12]

    today = date.today()

    trend_months = []
    for month_delta in trends:
        relative = today + relativedelta(months=month_delta)
        new_date = date(relative.year, relative.month, monthrange(relative.year, relative.month)[1])
        trend_months.append(new_date)

    delta_months = []
    for month_delta in deltas:
        relative = today + relativedelta(months=month_delta)
        new_date = date(relative.year, relative.month, monthrange(relative.year, relative.month)[1])
        delta_months.append(new_date)

    total_asset_data = _calculate_payload(asset_definitions, delta_months, trend_months)
    total_liability_data = _calculate_payload(liability_definitions, delta_months, trend_months)

    # Now to calculate the values for the net worth display
    net_worth_data = {'current_data': total_asset_data['current_data'] + total_liability_data['current_data'],
                      'deltas': [], 'trend': []}
    for index, trend in enumerate(trend_months):
        assets = total_asset_data['trend'][index]
        expenses = total_liability_data['trend'][index]
        net_worth_data['trend'].append(assets + expenses)

    for index, delta in enumerate(delta_months):
        assets = total_asset_data['delta_sub_total'][index]
        liability = total_liability_data['delta_sub_total'][index]
        net_value = assets + liability

        try:
            delta = (net_worth_data['current_data'] - net_value)
            result = (delta / net_worth_data['current_data']).copy_sign(delta)
            net_worth_data['deltas'].append(result)
        except:
            net_worth_data['deltas'].append('N/A')

    results = {
        'trend': [time.mktime(t.timetuple()) for t in trend_months],
        'deltas': deltas,
        'assets': total_asset_data,
        'liability': total_liability_data,
        'net_worth': net_worth_data
    }

    return results


def _calculate_payload(account_list, delta_months, trend_months):
    """
    Calculate the delta and trend values for the account list provided.
    :param account_list: account walker parameters with additional field 'name'
    :param delta_months: list of delta months to calculate
    :param trend_months: list of trend months to calculate
    :return: dictionary containing
    records - the list of sub accounts stored in the report containing
        name - the name of the record
        current_data - the current value in the account
        deltas - a list of the value in the account for the deltas
        trend - a list of the value in the account for the trend query
    current_data - the current value of all the records
    deltas - the list of the deltas for all the records
    trend - the list of the trends for all the records
    """
    currency = get_currency()
    today = date.today()
    end_of_month = date(today.year, today.month, monthrange(today.year, today.month)[1])
    total_data = {'records': [], 'current_data': Decimal('0.0'), 'deltas': [Decimal('0.0')] * len(delta_months),
                  'delta_sub_total': [Decimal('0.0')] * len(delta_months),
                  'trend': [Decimal('0.0')] * len(trend_months)}

    for definition in account_list:
        definition_data = {'name': definition['name'], 'current_data': Decimal('0.0'),
                           'deltas': [Decimal('0.0')] * len(delta_months),
                           'trend': [Decimal('0.0')] * len(trend_months)}

        # Get Current Data first
        for account in account_walker(**parse_walker_parameters(definition)):
            balance = get_balance_on_date(account, end_of_month, currency)
            definition_data['current_data'] += balance
            total_data['current_data'] += balance

        # Calculate the trends
        for index, trend in enumerate(trend_months):
            for account in account_walker(**parse_walker_parameters(definition)):
                balance = get_balance_on_date(account, trend, currency)
                definition_data['trend'][index] += balance
                total_data['trend'][index] += balance

        # Calculate deltas
        for index, delta in enumerate(delta_months):
            value = Decimal(0.0)
            for account in account_walker(**parse_walker_parameters(definition)):
                balance = get_balance_on_date(account, delta, currency)
                value += balance

                # Store the balance in the subtotal delta as well so don't have to fetch the data again.
                total_data['delta_sub_total'][index] += balance

            try:
                delta = definition_data['current_data'] - value
                definition_data['deltas'][index] = (delta / value).copy_sign(delta)
            except:
                definition_data['deltas'][index] = 'N/A'

        total_data['records'].append(definition_data)

    # Calculate the deltas for the total values.
    for index, value in enumerate(total_data['delta_sub_total']):
        try:
            delta = total_data['current_data'] - value
            total_data['deltas'][index] = (delta / value).copy_sign(delta)
        except:
            total_data['deltas'][index] = 'N/A'

    return total_data
