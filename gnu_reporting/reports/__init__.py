from gnu_reporting.reports.savings_goals import SavingsGoal, SavingsGoalTrend
from gnu_reporting.reports.account_levels import AccountLevels
from gnu_reporting.reports.budget_level import BudgetLevel
from gnu_reporting.reports.investment_balance import InvestmentBalance
from gnu_reporting.reports.federal_income import FederalIncomeTax
from gnu_reporting.reports.retirement_401k import Retirement401kReport
from gnu_reporting.reports.expenses_monthly import ExpensesMonthly, ExpensesMonthlyBox
from gnu_reporting.reports.cash_flow import MonthlyCashFlow
from gnu_reporting.reports.credit.credit_usage import CreditUsage

from gnu_reporting.reports.base import register_plugin, get_report


def register_core_reports():

    register_plugin(SavingsGoal)
    register_plugin(SavingsGoalTrend)
    register_plugin(AccountLevels)
    register_plugin(BudgetLevel)
    register_plugin(InvestmentBalance)
    register_plugin(FederalIncomeTax)
    register_plugin(Retirement401kReport)
    register_plugin(ExpensesMonthly)
    register_plugin(ExpensesMonthlyBox)
    register_plugin(MonthlyCashFlow)
    register_plugin(CreditUsage)
