from gnucash import Session, GncNumeric, Split
from decimal import Decimal
import time
from datetime import date

gnucash_session = None


def initialize(file_uri):
    global gnucash_session
    gnucash_session = Session(file_uri, is_new=False)
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
