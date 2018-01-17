from datetime import datetime
from decimal import Decimal
from gnucash_reports.configuration.current_date import get_today
from gnucash_reports.utilities import clean_account_name

import enum
import piecash
import re


@enum.unique
class AccountTypes(enum.Enum):
    none = 'NONE'
    bank = 'BANK'
    cash = 'CASH'
    credit = 'CREDIT'
    asset = 'ASSET'
    liability = 'LIABILITY'
    stock = 'STOCK'
    mutual_fund = 'MUTUAL'
    currency = 'CURRENCY'
    income = 'INCOME'
    expense = 'EXPENSE'
    equity = 'EQUITY'
    accounts_receivable = 'ACCOUNTS_RECEIVABLE'
    accounts_payable = 'ACCOUNTS_PAYABLE'
    root = 'ROOT'
    trading = 'TRADING'


gnucash_session = None

_account_cache = dict()


def initialize(file_uri, read_only=True, do_backup=False):
    global gnucash_session
    gnucash_session = piecash.open_book(uri_conn=file_uri, open_if_lock=True, readonly=read_only, do_backup=do_backup)
    return gnucash_session


def get_session():
    return gnucash_session


def get_account(account_name):
    global _account_cache
    current_account = gnucash_session.root_account

    current_account_name = ''

    for child_name in re.split('[:.]', account_name):

        if current_account_name:
            current_account_name = current_account_name + '.' + child_name
        else:
            current_account_name = child_name

        account = _account_cache.get(current_account_name, None)

        if account is None:
            account = gnucash_session.session.query(piecash.Account).filter(piecash.Account.parent == current_account,
                                                                            piecash.Account.name == child_name).one_or_none()

            if account is None:
                raise RuntimeError('Account %s is not found in %s' % (account_name, current_account))

            _account_cache[current_account_name] = account

        current_account = account

    return current_account


def get_splits(account, start_date, end_date=None, credit=True, debit=True):

    start_time = datetime.combine(start_date, datetime.min.time())
    if not end_date:
        end_date = get_today()

    end_time = datetime.combine(end_date, datetime.max.time())

    start_time = start_time.replace(microsecond=0, tzinfo=None)
    end_time = end_time.replace(microsecond=0, tzinfo=None)

    result = []

    split_query = gnucash_session.session.query(piecash.Split).filter(
        piecash.Split.account == account,
        piecash.Split.transaction.has(piecash.Transaction.post_date >= start_time),
        piecash.Split.transaction.has(piecash.Transaction.post_date <= end_time)
    )

    for split in split_query:
        is_credit = split.value > 0

        if credit and is_credit:
            result.append(split)
        elif debit and not is_credit:
            result.append(split)

    return result


def account_walker(accounts, ignores=None, place_holders=False, recursive=True, **kwargs):
    """
    Generator method that will recursively walk the list of accounts provided, ignoring the accounts that are in the
    ignore list.
    :param accounts:
    :param ignores:
    :param recursive:
    :param place_holders:
    :return:
    """
    if not ignores:
        ignores = []

    _account_list = [a for a in accounts]

    ignores = [clean_account_name(account_name) for account_name in ignores]

    while _account_list:
        account_name = _account_list.pop()
        if account_name in ignores:
            continue

        account = get_account(account_name)
        if not account.placeholder or place_holders:
            yield account

        if recursive:
            _account_list += [clean_account_name(a.fullname) for a in account.children]


def parse_walker_parameters(definition):
    """
    convert the incoming definition into a kwargs that can be used for the account walker.
    :param definition:
    :return:
    """
    return_value = {
        'ignores': None,
        'place_holders': False,
        'recursive': True
    }

    if isinstance(definition, dict):
        return_value.update(definition)
    elif isinstance(definition, list) or isinstance(definition, set):
        return_value.update(accounts=list(definition))
    else:
        return_value.update(accounts=[definition])

    return return_value


def get_balance_on_date(account, date_value=get_today(), currency=None):

    date_value = datetime.combine(date_value, datetime.max.time()).replace(microsecond=0, tzinfo=None)

    splits = gnucash_session.session.query(piecash.Split).filter(
        piecash.Split.account == account,
        piecash.Split.transaction.has(piecash.Transaction.post_date < date_value)
    ).all()

    if splits:
        balance_decimal = sum([s.quantity for s in splits])

        if currency:
            # If the account_commodity and the currency are the same value, then just ignore fetching the value from the
            # database.
            if currency.mnemonic != account.commodity.mnemonic:

                price_value = gnucash_session.session.query(piecash.Price).filter(
                    piecash.Price.commodity == account.commodity,
                    piecash.Price.currency == currency,
                    piecash.Price.date <= date_value,
                ).order_by(piecash.Price.date.desc()).limit(1).one_or_none()

                if price_value:
                    # print date_value, account.fullname, balance_decimal, price_value.value
                    balance_decimal = balance_decimal * price_value.value
                else:
                    print currency, account.commodity, date_value
                    raise NotImplementedError('Couldn\'t find a valid value')
    else:
        balance_decimal = Decimal(0.0)

    return balance_decimal


def get_corr_account_full_name(split):
    """
    Iterate through the parent splits and return all of the accounts that have a value in the opposite sign of the value
    in split.
    :param split:
    :return:
    """
    return_value = []

    signed = split.value.is_signed()

    for child_split in split.transaction.splits:
        split_value = child_split.value

        if signed != split_value.is_signed():
            return_value.append(child_split.account)

    if not return_value:
        raise RuntimeError('Couldn\'t find opposite accounts.')

    if len(return_value) > 1:
        print 'return_value: ', return_value
        raise RuntimeError('Split returned more than one correlating account')

    return return_value[0].fullname


def get_prices(commodity, currency):
    """
    Return all of the prices for a specific commodity in the currency provided.
    :param commodity:
    :param currency:
    :return:
    """
    price_list = gnucash_session.session.query(piecash.Price).filter(
        piecash.Price.commodity == commodity,
        piecash.Price.currency == currency
        ).order_by(piecash.Price.date.desc()).all()

    return price_list
