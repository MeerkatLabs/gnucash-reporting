import piecash
import re
from datetime import datetime
import enum


@enum.unique
class AccountTypes(enum.Enum):
    none = 'NONE'
    bank = 'BANK'
    cash = 'CASH'
    credit = 'CREDIT'
    asset = 'ASSET'
    liability = 'LIABILITY'
    stock = 'STOCK'
    mutual_fund = 'MUTUAL_FUND'
    currency = 'CURRENCY'
    income = 'INCOME'
    expense = 'EXPENSE'
    equity = 'EQUITY'
    accounts_receivable = 'ACCOUNTS_RECEIVABLE'
    accounts_payable = 'ACCOUNTS_PAYABLE'
    root = 'ROOT'
    trading = 'TRADING'


gnucash_session = None


def initialize(file_uri):
    global gnucash_session
    gnucash_session = piecash.open_book(uri_conn=file_uri)
    return gnucash_session


def get_session():
    return gnucash_session


def get_account(account_name):
    current_account = gnucash_session.root_account

    for child_name in re.split('[:.]', account_name):
        account = gnucash_session.session.query(piecash.Account).filter(piecash.Account.parent == current_account,
                                                                        piecash.Account.name == child_name).one_or_none()

        if account is None:
            raise RuntimeError('Account %s is not found in %s' % (account_name, current_account))

        current_account = account

    return current_account


def get_decimal(numeric):
    raise NotImplementedError('Stop using this code')
    # try:
    #     return Decimal(numeric.num()) / Decimal(numeric.denom())
    # except TypeError:
    #     return Decimal(numeric.num) / Decimal(numeric.denom)


def get_splits(account, start_date, end_date=None, credit=True, debit=True):

    start_time = datetime.combine(start_date, datetime.min.time())
    if not end_date:
        end_date = datetime.today()

    end_time = datetime.combine(end_date, datetime.min.time())

    result = []

    split_query = gnucash_session.session.query(piecash.Split).filter(
        piecash.Split.account == account,
        piecash.Split.transaction.has(piecash.Transaction.post_date <= start_time),
        piecash.Split.transaction.has(piecash.Transaction.post_date >= end_time)
    )

    for split in split_query:
        is_credit = split.value > 0

        if credit and is_credit:
            result.append(split)
        elif debit and not is_credit:
            result.append(split)

    return result


def account_walker(account_list, ignore_list=None, place_holders=False, recursive=True):
    """
    Generator method that will recursively walk the list of accounts provided, ignoring the accounts that are in the
    ignore list.
    :param account_list:
    :param ignore_list:
    :param place_holders:
    :return:
    """
    if not ignore_list:
        ignore_list = []

    _account_list = [a for a in account_list]

    while _account_list:
        account_name = _account_list.pop()
        if account_name in ignore_list:
            continue

        account = get_account(account_name)
        if not account.placeholder or place_holders:
            yield account

        if recursive:
            _account_list += [a.fullname for a in account.children]

        break


def get_balance_on_date(account, date_value, currency=None):

    date_value = datetime.combine(date_value, datetime.min.time())

    split_query = gnucash_session.session.query(piecash.Split).filter(
        piecash.Split.transaction.has(piecash.Transaction.post_date < date_value)
    )

    balance_decimal = sum([s.value for s in split_query]) * account.sign

    if currency:
        # If the account_commodity and the currency are the same value, then just ignore fetching the value from the
        # database.
        if currency.mnemonic != account.commodity.mnemonic:

            print currency.mnemonic
            print account.commodity.mnemonic

            print date_value

            price_value = gnucash_session.session.query(piecash.Price).filter(
                piecash.Price.commodity == account.commodity,
                piecash.Price.date <= date_value
            ).order_by(piecash.Price.date.desc()).limit(1).one_or_none()

            print price_value

            raise NotImplemented('Not implemented yet')

    return balance_decimal

    # today_time = time.mktime(date_value.timetuple())
    #
    # balance = account.GetBalanceAsOfDate(today_time)
    # balance_decimal = get_decimal(balance)
    #
    # if currency:
    #     account_commodity = account.GetCommodity()
    #     price_db = gnucash_session.get_book().get_price_db()
    #
    #     # If the account_commodity and the currency are the same value, then just ignore fetching the value from the
    #     # database.
    #     if account_commodity.get_mnemonic() != currency.get_mnemonic():
    #         # The API of this call is different than the get balance as of date, takes an actual date datetime object.
    #         price = price_db.lookup_latest_before(account_commodity, currency, date_value)
    #
    #         # Just in case the price couldn't be found based on the date provided, use the nearest value, even if it's
    #         # in the future.
    #         if price is None:
    #             price = price_db.lookup_nearest_in_time(account_commodity, currency, date_value)
    #
    #         balance_decimal *= get_decimal(price.get_value())
    #
    # return balance_decimal


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
        raise RuntimeError('Split returned more than one correlating account')

    return return_value[0].fullname
