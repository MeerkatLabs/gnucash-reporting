"""
Gather information about the balance of the investment accounts.
"""
import time
from decimal import Decimal
from operator import itemgetter

from dateutils import relativedelta

from gnucash_reports.collate.bucket import PeriodCollate
from gnucash_reports.configuration.current_date import get_today
from gnucash_reports.configuration.currency import get_currency
from gnucash_reports.configuration.investment_allocations import get_asset_allocation
from gnucash_reports.periods import PeriodStart, PeriodEnd, PeriodSize
from gnucash_reports.wrapper import get_account, get_balance_on_date, AccountTypes, \
    account_walker, get_splits, get_corr_account_full_name, get_prices, parse_walker_parameters


def investment_balance(definition):
    account = get_account(definition['account'])

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
            previous_date_key = time.mktime(previous_date.timetuple())
            purchases[previous_date_key] = last_purchase
            dividends[previous_date_key] = last_dividend
            values[previous_date_key] = get_balance_on_date(account, previous_date, currency)

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

        key = time.mktime(date.timetuple())
        purchases[key] = last_purchase
        dividends[key] = last_dividend
        values[key] = get_balance_on_date(account, date, currency)

    # Now get all of the price updates in the database.
    for price in get_prices(account.commodity, currency):
        date = time.mktime(price.date.timetuple())

        values[date] = max(values.get(date, Decimal('0.0')),
                           get_balance_on_date(account, price.date, currency))

    return dict(purchases=sorted([(key, value) for key, value in purchases.iteritems()], key=itemgetter(0)),
                dividend=sorted([(key, value) for key, value in dividends.iteritems()], key=itemgetter(0)),
                value=sorted([(key, value) for key, value in values.iteritems()], key=itemgetter(0)))


def investment_bucket_generator():
    return dict(money_in=Decimal('0.0'), income=Decimal('0.0'), expense=Decimal('0.0'))


def store_investment(bucket, value):
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
        print 'Unknown account type: %s' % account_type

    return bucket


def investment_trend(definition):
    investment_accounts = parse_walker_parameters(definition.get('investment_accounts', []))
    period_start = PeriodStart(definition.get('period_start', PeriodStart.this_month_year_ago))
    period_end = PeriodEnd(definition.get('period_end', PeriodEnd.this_month))
    period_size = PeriodSize(definition.get('period_size', PeriodSize.month))

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
        'income': sorted(
            [(time.mktime(key.timetuple()), value['income']) for key, value in buckets.container.iteritems()],
            key=itemgetter(0)),
        'money_in': sorted(
            [(time.mktime(key.timetuple()), value['money_in']) for key, value in buckets.container.iteritems()],
            key=itemgetter(0)),
        'expense': sorted(
            [(time.mktime(key.timetuple()), value['expense']) for key, value in buckets.container.iteritems()],
            key=itemgetter(0)),
        'value': sorted(
            [[time.mktime(key.timetuple()), value] for key, value in investment_value.iteritems()],
        ),
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


def investment_allocation(definition):
    investment_accounts = parse_walker_parameters(definition.get('investment_accounts', []))
    category_mapping = definition.get('category_mapping', {})

    breakdown = dict()
    today = get_today()
    currency = get_currency()

    for account in account_walker(**investment_accounts):
        balance = get_balance_on_date(account, today, currency)
        commodity = account.commodity.mnemonic

        results = get_asset_allocation(commodity, balance)

        for key, value in results.iteritems():
            breakdown[key] = breakdown.get(key, Decimal('0.0')) + value

    return dict(categories=sorted([[category_mapping.get(key, key), value] for key, value in breakdown.iteritems()],
                                  key=itemgetter(0)))
