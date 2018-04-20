from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, YEARLY, DAILY, WEEKLY
from enum import Enum
from gnucash_reports.configuration.current_date import get_today


class PeriodStart(Enum):
    """
    Enumeration that can be used for defining and calculating a period start value.
    """
    today = 'today'
    this_month = 'start_of_this_month'
    previous_month = 'start_of_previous_month'
    this_quarter = 'start_of_this_quarter'
    previous_quarter = 'start_of_previous_quarter'
    this_year = 'start_of_this_year'
    previous_year = 'start_of_previous_year'
    this_month_year_ago = 'start_of_this_month_year_ago'
    start = 'start'

    @property
    def date(self):
        """ The date associated with the period start based on the configuration value of what today is. """
        today = get_today()

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
        elif self == PeriodStart.start:
            return date(1970, 1, 1)


class PeriodEnd(Enum):
    """
    Enumeration for defining and calculating the date for period end value.
    """
    today = 'today'
    this_month = 'end_of_this_month'
    previous_month = 'end_of_previous_month'
    this_quarter = 'end_of_this_quarter'
    previous_quarter = 'end_of_previous_quarter'
    this_year = 'end_of_this_year'
    previous_year = 'end_of_previous_year'
    end = 'end'

    @property
    def date(self):
        """ The date associated with the period end based on the configuration value of what today is. """
        today = get_today()

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
        elif self == PeriodEnd.previous_year:
            return date(today.year - 1, 12, 31)
        elif self == PeriodEnd.end:
            return date(today.year + 1, 12, 31)


class PeriodSize(Enum):
    """
    Enumeration for defining the step size between a period start and period end value.
    """
    day = 'day'
    week = 'week'
    two_week = 'two_week'
    month = 'month'
    year = 'year'

    @property
    def frequency(self):
        """Returns dateutil.rrule associated with the enumeration."""
        if self == PeriodSize.day:
            return DAILY
        elif self == PeriodSize.week or self == PeriodSize.two_week:
            return WEEKLY
        elif self == PeriodSize.month:
            return MONTHLY
        elif self == PeriodSize.YEARLY:
            return YEARLY

        else:
            raise KeyError('Unknown enumeration')

    @property
    def interval(self):
        """Returns a value that acts as a multiplier for the rrule value."""
        if self == PeriodSize.two_week:
            return 2
        else:
            return 1
