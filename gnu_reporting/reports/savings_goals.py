from datetime import datetime
import time
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
from gnu_reporting.reports.base import Report
from gnu_reporting.wrapper import get_decimal, get_account, get_balance_on_date
from gnu_reporting.periods import PeriodStart
from gnu_reporting.configuration.currency import get_currency
import simplejson as json
from decimal import Decimal


class SavingsGoal(Report):
    report_type = 'savings_goal'

    def __init__(self, name, account, goal, as_of=PeriodStart.today):
        super(SavingsGoal, self).__init__(name)

        if isinstance(account, basestring):
            account = [account]

        self.accounts = account
        self.goal_amount = goal

        self.as_of = PeriodStart(as_of)

    def __call__(self):

        total_balance = Decimal('0.0')
        currency = get_currency()

        for account_name in self.accounts:
            multiplier = Decimal('1.0')
            if isinstance(account_name, basestring):
                account = get_account(account_name)
            else:
                account = get_account(account_name[0])
                multiplier = Decimal(account_name[1])

            balance = get_balance_on_date(account, self.as_of.date, currency)
            total_balance += (balance * multiplier)

        payload = self._generate_result()
        payload['data']['balance'] = total_balance
        payload['data']['goal'] = self.goal_amount

        return payload


class SavingsGoalTrend(Report):
    report_type = 'savings_goal_trend'

    def __init__(self, name, account_name, goal_amount, past_trend=12, future_trend=6):
        super(SavingsGoalTrend, self).__init__(name)
        self.account_name = account_name
        self.goal_amount = goal_amount
        self.past_trend = past_trend
        self.future_trend = future_trend

    def __call__(self):

        account = get_account(self.account_name)

        todays_date = datetime.today()
        beginning_of_month = datetime(todays_date.year, todays_date.month, 1)

        start_of_trend = beginning_of_month - relativedelta(months=self.past_trend)
        end_of_trend = start_of_trend + relativedelta(months=self.past_trend + self.future_trend)

        payload = self._generate_result()
        payload['data']['trend'] = []

        for dt in rrule(MONTHLY, dtstart=start_of_trend, until=end_of_trend):
            time_value = time.mktime(dt.timetuple())

            balance = account.GetBalanceAsOfDate(time_value)
            payload['data']['trend'].append(dict(date=dt.strftime('%Y-%m-%d'),
                                                 balance=get_decimal(balance)))

        return payload


if __name__ == '__main__':

    from gnu_reporting.wrapper import initialize
    from decimal import Decimal

    session = initialize('data/Accounts.gnucash')
    goal_amount = Decimal('25904.12')

    report = SavingsGoalTrend('Estimated Taxes', 'Assets.Savings Goals.Estimated Taxes 2015', goal_amount)
    payload = report()

    other_report = SavingsGoal('Estimated Taxes', 'Assets.Savings Goals.Estimated Taxes 2015', goal_amount)
    other_payload = other_report()

    session.end()

    print json.dumps(payload)
    print ''
    print json.dumps(other_payload)
