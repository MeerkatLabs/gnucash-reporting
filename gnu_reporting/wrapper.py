from gnucash import Session, GncNumeric, Split
from decimal import Decimal
import time
from datetime import date

gnucash_session = None
currency_value = None


def initialize(file_uri, account_with_currency=None):
    global gnucash_session, currency_value
    gnucash_session = Session(file_uri, is_new=False)

    if account_with_currency:
        currency_value = get_account(account_with_currency).GetCommodity()

    return gnucash_session


def get_session():
    return gnucash_session


def get_account(account_name):

    account = gnucash_session.get_book().get_root_account().lookup_by_full_name(account_name)

    if account is None:
        raise RuntimeError('Account %s is not found' % account_name)

    return account


def get_decimal(numeric):
    return Decimal(numeric.num()) / Decimal(numeric.denom())


def get_splits(account, start_date, end_date=None, credit=True, debit=True):

    start_time = time.mktime(start_date.timetuple())
    if not end_date:
        end_date = date.today()

    end_time = time.mktime(end_date.timetuple())

    result = []

    for split in account.GetSplitList():
        split_date = split.parent.GetDate()

        if start_time <= split_date < end_time:

            is_credit = split.GetAmount().num() > 0

            if credit and is_credit:
                result.append(split)
            elif debit and not is_credit:
                result.append(split)

    return result


def account_walker(account_list, ignore_list=None, place_holders=False):
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
        if not account.GetPlaceholder() or place_holders:
            yield account

        _account_list += [a.get_full_name() for a in account.get_children()]


def get_currency():
    return currency_value
