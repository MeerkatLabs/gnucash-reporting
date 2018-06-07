"""
Gather information about the balance of the investment accounts.
"""
import time
from decimal import Decimal

from dateutils import relativedelta
from operator import itemgetter

from gnucash_reports.collate.bucket import PeriodCollate
from gnucash_reports.configuration.current_date import get_today
from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.configuration.investment_allocations import get_asset_allocation
from gnucash_reports.periods import PeriodStart, PeriodEnd, PeriodSize
from gnucash_reports.wrapper import get_account, get_balance_on_date, AccountTypes, \
    account_walker, get_splits, get_corr_account_full_name, get_prices, parse_walker_parameters
from gnucash_reports.utilities import time_series_dict_to_list


def investment_balance(account):
    """
    Generate report that calculates purchases, dividends, and current worth of the investment accounts provided.
    :param account: investment account definition
    :return: dictionary giving time series for the following information
    value - date/value tuples containing value in currency
    purchases - date/value tuples containing purchase information in currency
    dividend - date/value tuples containing dividend information in currency
    """
    # TODO: Change this to be account walker parameters
    account = get_account(account)

    last_dividend = Decimal('0.0')
    last_purchase = Decimal('0.0')

    currency = get_currency()

    purchases = dict()
    dividends = dict()
    values = dict()

    for split in sorted(account.splits, key=lambda x: x.transaction.post_date):
        other_account_name = get_corr_account_full_name(split)
        other_account = get_account(other_account_name)

        account_type = AccountTypes(other_account.type.upper())
        date = split.transaction.post_date

        # Store previous data
        if len(purchases):
            previous_date = date - relativedelta(days=1)
            purchases[previous_date] = last_purchase
            dividends[previous_date] = last_dividend
            values[previous_date] = get_balance_on_date(account, previous_date, currency)

        # Find the correct amount that was paid from the account into this account.
        change_amount = split.value

        if change_amount > 0:
            # Need to get the value from the corr account split.
            for parent_splits in split.transaction.splits:
                if parent_splits.account.fullname == other_account_name:
                    change_amount = -parent_splits.value

        if account_type == AccountTypes.mutual_fund or account_type == AccountTypes.asset:
            # Asset or mutual fund transfer
            last_purchase += change_amount
        else:
            last_dividend += split.value

        purchases[date] = last_purchase
        dividends[date] = last_dividend
        values[date] = get_balance_on_date(account, date, currency)

    # Sort the purchases and dividends so can keep track of purchases and dividends while the current value is
    # being put into place.  Because this is not the final value of the list, don't need to worry about converting the
    # dates into floats.
    sorted_purchases = time_series_dict_to_list(purchases, key=None)
    sorted_dividend = time_series_dict_to_list(dividends, key=None)

    # Index of where in the sorted purchases and dividends we are when updating the values
    sorted_index = 0
    sorted_length = len(sorted_purchases)

    # Now get all of the price updates in the database.
    for price in get_prices(account.commodity, currency):
        date = price.date

        # Find out where in the purchases/dividends this record would fall by iterating through the sorted list until
        # we pass the current date value, then use the previous key
        test_sorted_index = sorted_index
        while test_sorted_index < sorted_length and sorted_purchases[test_sorted_index][0] <= date:
            test_sorted_index += 1

        # Skip the first record, it's already handled by the purchase population code.  Otherwise put in placeholder
        # data so that the number of records is the same in all of the data structures.
        if test_sorted_index != 0:
            purchases[date] = sorted_purchases[test_sorted_index-1][1]
            dividends[date] = sorted_dividend[test_sorted_index-1][1]
            values[date] = max(values.get(date, Decimal('0.0')), get_balance_on_date(account, price.date, currency))

    # Resort all of the dictionaries into the appropriate pairs so that the data is displayed correctly by the
    # viewer.
    values = time_series_dict_to_list(values)
    purchases = time_series_dict_to_list(purchases)
    dividend = time_series_dict_to_list(dividends)

    return {'purchases': purchases, 'dividend': dividend, 'value': values}


def investment_bucket_generator():
    """
    Bucket generator that will store purchases, income and expenses for the transactions into an account.
    :return: dictionary containing the default values of the buckets.
    """
    return {'money_in': Decimal('0.0'), 'income': Decimal('0.0'), 'expense': Decimal('0.0')}


def store_investment(bucket, value):
    """
    How to store the split information into the bucket provided.
    :param bucket: bucket for the time value that the split belongs to
    :param value: transaction split object
    :return: bucket
    """
    other_account_name = get_corr_account_full_name(value)
    other_account = get_account(other_account_name)

    account_type = AccountTypes(other_account.type.upper())

    # Find the correct amount that was paid from the account into this account.
    change_amount = value.value

    if change_amount > 0:
        # Need to get the value from the corr account split.
        for parent_splits in value.transaction.splits:
            if parent_splits.account.fullname == other_account_name:
                change_amount = -parent_splits.value

    if account_type == AccountTypes.mutual_fund or account_type == AccountTypes.asset or \
       account_type == AccountTypes.equity or account_type == AccountTypes.stock:
        # Asset or mutual fund transfer
        bucket['money_in'] += change_amount
    elif account_type == AccountTypes.income:
        bucket['income'] += value.value
    elif account_type == AccountTypes.expense:
        bucket['expense'] += value.value
    else:
        print(f'Unknown account type: {account_type}')

    return bucket


def investment_trend(investment_accounts=None, start=PeriodStart.this_month_year_ago, end=PeriodEnd.this_month,
                     period_size=PeriodSize.month):
    """
    Report showing how the investment has changed over a period of time.  This report provides data based on the period
    size provided in the arguments.
    :param investment_accounts: account walker parameters for all of the accounts that this report should provide
    data on
    :param start: the start time frame of the report
    :param end: the end time frame of the report
    :param period_size: the step size between start and end
    :return: dictionary containing the following
    start_value - no clue
    income - time series data containing the income generated by account (dividends)
    money_in - time series data containing the purchases into the accounts
    expense - time series data containing the expenses of the accounts
    value - time series data containing the current value of the accounts
    basis - time series data containing the basis value of the accounts (not sure if this is correct)
    """

    # TODO: Figure out what this report is really doing with start_value and basis values. Verify they are calculated
    # correctly.
    investment_accounts = investment_accounts or []

    investment_accounts = parse_walker_parameters(investment_accounts)
    period_start = PeriodStart(start)
    period_end = PeriodEnd(end)
    period_size = PeriodSize(period_size)

    investment_value = dict()
    buckets = PeriodCollate(period_start.date, period_end.date,
                            investment_bucket_generator, store_investment, frequency=period_size.frequency,
                            interval=period_size.interval)

    start_value = Decimal('0.0')
    start_value_date = period_start.date - relativedelta(days=1)
    currency = get_currency()

    for account in account_walker(**investment_accounts):
        for split in get_splits(account, period_start.date, period_end.date):
            buckets.store_value(split)

        start_value += get_balance_on_date(account, start_value_date, currency)

        for key in buckets.container.keys():
            date_value = key + relativedelta(months=1) - relativedelta(days=1)
            investment_value[key] = investment_value.get(key, Decimal('0.0')) + get_balance_on_date(account,
                                                                                                    date_value,
                                                                                                    currency)

    results = {
        'start_value': start_value,
        'income': time_series_dict_to_list(buckets.container, value=lambda x: x['income']),
        'money_in': time_series_dict_to_list(buckets.container, value=lambda x: x['money_in']),
        'expense': time_series_dict_to_list(buckets.container, value=lambda x: x['expense']),
        'value': time_series_dict_to_list(investment_value),
        'basis': sorted(
            [[time.mktime(key.timetuple()), Decimal('0.0')] for key in buckets.container.keys()],
            key=itemgetter(0))
    }

    monthly_start = start_value
    for index, record in enumerate(results['basis']):
        record[1] += (monthly_start + results['income'][index][1] + results['money_in'][index][1] +
                      results['expense'][index][1])
        monthly_start = record[1]

    return results


def investment_allocation(investment_accounts=None):
    """
    Investment allocation report.  Walks through all of the investment accounts and determines the breakdowns of the
    assets based on the category mapping data.
    :param investment_accounts: the accounts to walk through when calculation asset breakdown
    :return: dictionary containing
    categories - list of tuples containing human readable term key to the value contained in the investment accounts.
    """
    investment_accounts = investment_accounts or []

    investment_accounts = parse_walker_parameters(investment_accounts)

    breakdown = dict()
    today = get_today()
    currency = get_currency()

    for account in account_walker(**investment_accounts):
        balance = get_balance_on_date(account, today, currency)
        commodity = account.commodity.mnemonic

        results = get_asset_allocation(commodity, balance)

        for key, value in results.items():
            breakdown[key] = breakdown.get(key, Decimal('0.0')) + value

    return dict(categories=sorted([[key.replace('_', ' ').title(), value] for key, value in breakdown.items()],
                                  key=itemgetter(0)))
