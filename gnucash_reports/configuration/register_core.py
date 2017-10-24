"""
Register the core reports and configuration details for the framework.
"""


def register_core_reports():
    """Entry point that registers core reports."""
    from gnucash_reports.reports.savings_goals import SavingsGoal, SavingsGoalTrend
    from gnucash_reports.reports.account_levels import AccountLevels
    from gnucash_reports.reports.budget_level import BudgetLevel, BudgetPlanning, CategoryBudgetLevel
    from gnucash_reports.reports.investment_balance import InvestmentBalance, InvestmentTrend, InvestmentAllocation
    from gnucash_reports.reports.income_tax import IncomeTax
    from gnucash_reports.reports.retirement_401k import Retirement401kReport
    from gnucash_reports.reports.expenses_monthly import ExpensesMonthly, ExpensesMonthlyBox, ExpenseCategories, \
        ExpenseAccounts
    from gnucash_reports.reports.cash_flow import MonthlyCashFlow
    from gnucash_reports.reports.credit.credit_usage import CreditUsage, DebtVsLiquidAssets
    from gnucash_reports.reports.net_worth import NetWorthCalculator, NetWorthTable
    from gnucash_reports.reports.account_usage_categories import AccountUsageCategories
    from gnucash_reports.reports.income_expenses import IncomeVsExpense

    from gnucash_reports.reports.base import register_plugin

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
    register_plugin(ExpenseAccounts)
    register_plugin(MonthlyCashFlow)
    register_plugin(CreditUsage)
    register_plugin(DebtVsLiquidAssets)
    register_plugin(NetWorthCalculator)
    register_plugin(NetWorthTable)
    register_plugin(AccountUsageCategories)
    register_plugin(IncomeVsExpense)


def register_core_configuration_plugins():
    """Entry points that registers all of the core configuration plugins."""
    from gnucash_reports.configuration.base import register_configuration_plugin as _register_configuration_plugin
    from gnucash_reports.configuration.currency import configure as _configure_currency
    from gnucash_reports.configuration.inflation import configure as _configure_inflation
    from gnucash_reports.configuration.tax_tables import configure_tax_tables
    from gnucash_reports.configuration.expense_categories import configure as _configure_expense_categories
    from gnucash_reports.configuration.investment_allocations import configure as _configure_investment_allocations
    _register_configuration_plugin(_configure_currency)
    _register_configuration_plugin(_configure_inflation)
    _register_configuration_plugin(configure_tax_tables)
    _register_configuration_plugin(_configure_expense_categories)
    _register_configuration_plugin(_configure_investment_allocations)
