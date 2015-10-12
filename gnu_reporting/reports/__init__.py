from gnu_reporting.reports.savings_goals import SavingsGoal, SavingsGoalTrend
from gnu_reporting.reports.account_levels import AccountLevels
from gnu_reporting.reports.budget_level import BudgetLevel, BudgetPlanning, CategoryBudgetLevel
from gnu_reporting.reports.investment_balance import InvestmentBalance, InvestmentTrend, InvestmentAllocation
from gnu_reporting.reports.income_tax import IncomeTax
from gnu_reporting.reports.retirement_401k import Retirement401kReport
from gnu_reporting.reports.expenses_monthly import ExpensesMonthly, ExpensesMonthlyBox, ExpenseCategories
from gnu_reporting.reports.cash_flow import MonthlyCashFlow
from gnu_reporting.reports.credit.credit_usage import CreditUsage, DebtVsLiquidAssets
from gnu_reporting.reports.net_worth import NetWorthCalculator, NetWorthTable
from gnu_reporting.reports.account_usage_categories import AccountUsageCategories
from gnu_reporting.reports.income_expenses import IncomeVsExpense

from gnu_reporting.reports.base import register_plugin, get_report, build_report


def register_core_reports():

    register_plugin(SavingsGoal)
    register_plugin(SavingsGoalTrend)
    register_plugin(AccountLevels)
    register_plugin(BudgetLevel)
    register_plugin(BudgetPlanning)
    register_plugin(CategoryBudgetLevel)
    register_plugin(InvestmentBalance)
    register_plugin(InvestmentTrend)
    register_plugin(InvestmentAllocation)
    register_plugin(IncomeTax)
    register_plugin(Retirement401kReport)
    register_plugin(ExpensesMonthly)
    register_plugin(ExpensesMonthlyBox)
    register_plugin(ExpenseCategories)
    register_plugin(MonthlyCashFlow)
    register_plugin(CreditUsage)
    register_plugin(DebtVsLiquidAssets)
    register_plugin(NetWorthCalculator)
    register_plugin(NetWorthTable)
    register_plugin(AccountUsageCategories)
    register_plugin(IncomeVsExpense)
