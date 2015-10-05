from enum import Enum
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY


class PeriodStart(Enum):
    today = 'today'
    this_month = 'start_of_this_month'
    previous_month = 'start_of_previous_month'
    this_quarter = 'start_of_this_quarter'
    previous_quarter = 'start_of_previous_quarter'
    this_year = 'start_of_this_year'
    previous_year = 'start_of_previous_year'
    this_month_year_ago = 'start_of_this_month_year_ago'

    @property
    def date(self):
        today = datetime.today()

        if self == PeriodStart.today:
            return today.date()
        elif self == PeriodStart.this_month or self == PeriodStart.previous_month:
            this_month = date(today.year, today.month, 1)
            if self == PeriodStart.this_month:
                return this_month
            else:
                return this_month - relativedelta(months=1)
        elif self == PeriodStart.this_quarter or self == PeriodStart.previous_quarter:
            quarters = rrule(MONTHLY, bymonth=(1, 4, 7, 10),
                             bysetpos=-1,
                             dtstart=datetime(today.year-1, 1, 1),
                             count=12)
            quarter_first_day = quarters.before(today)

            if self == PeriodStart.this_quarter:
                return quarter_first_day.date()
            else:
                return quarters.before(quarter_first_day).date()
        elif self == PeriodStart.this_year:
            return date(today.year, 1, 1)
        elif self == PeriodStart.previous_year:
            return date(today.year - 1, 1, 1)
        elif self == PeriodStart.this_month_year_ago:
            return date(today.year-1, today.month, 1)


class PeriodEnd(Enum):
    today = 'today'
    this_month = 'end_of_this_month'
    previous_month = 'end_of_previous_month'
    this_quarter = 'end_of_this_quarter'
    previous_quarter = 'end_of_previous_quarter'
    this_year = 'end_of_this_year'
    previous_year = 'end_of_previous_year'

    @property
    def date(self):
        today = datetime.today()

        if self == PeriodEnd.today:
            return today.date()
        elif self == PeriodEnd.this_month or self == PeriodEnd.previous_month:
            this_month = date(today.year, today.month, 1)
            if self == PeriodEnd.this_month:
                return this_month + relativedelta(months=1) - relativedelta(days=1)
            else:
                return this_month - relativedelta(days=1)
        elif self == PeriodEnd.this_quarter or self == PeriodEnd.previous_quarter:
            quarters = rrule(MONTHLY, bymonth=(1, 4, 7, 10),
                             bysetpos=-1,
                             dtstart=datetime(today.year-1, 1, 1),
                             count=12)
            quarter_first_day = quarters.after(today)

            if self == PeriodEnd.this_quarter:
                return quarter_first_day.date() - relativedelta(days=1)
            else:
                return quarters.before(quarter_first_day).date() - relativedelta(days=1)
        elif self == PeriodEnd.this_year:
            return date(today.year, 12, 31)
        else:
            return date(today.year - 1, 12, 31)


class PeriodSize(Enum):
    day = 'day'
    week = 'week'
    two_week = 'two_week'
    month = 'month'
    year = 'year'

