"""
Register the core reports and configuration details for the framework.
"""


def register_core_reports():
    """Entry point that registers core reports."""
    from gnucash_reports.reports.savings_goals import savings_goal, savings_goal_trend
    from gnucash_reports.reports.account_levels import account_levels
    from gnucash_reports.reports.budget_level import budget_level, budget_planning, category_budget_level
    from gnucash_reports.reports.investment_balance import investment_balance, investment_trend, investment_allocation
    from gnucash_reports.reports.income_tax import income_tax
    from gnucash_reports.reports.retirement_401k import retirement_401k_report
    from gnucash_reports.reports.expenses_monthly import expenses_period, expenses_box, expenses_categories, \
        expense_accounts
    from gnucash_reports.reports.cash_flow import cash_flow
    from gnucash_reports.reports.credit.credit_usage import credit_usage, debt_vs_liquid_assets
    from gnucash_reports.reports.net_worth import net_worth, net_worth_table
    from gnucash_reports.reports.account_usage_categories import account_usage_categories
    from gnucash_reports.reports.income_expenses import income_vs_expense

    from gnucash_reports.reports.base import register_plugin, multi_report

    register_plugin(savings_goal)
    register_plugin(savings_goal_trend)
    register_plugin(account_levels)
    register_plugin(budget_level)
    register_plugin(budget_planning)
    register_plugin(category_budget_level)
    register_plugin(investment_balance)
    register_plugin(investment_trend)
    register_plugin(investment_allocation)
    register_plugin(income_tax)
    register_plugin(retirement_401k_report)
    register_plugin(expenses_period)
    register_plugin(expenses_box)
    register_plugin(expenses_categories)
    register_plugin(expense_accounts)
    register_plugin(cash_flow)
    register_plugin(credit_usage)
    register_plugin(debt_vs_liquid_assets)
    register_plugin(net_worth)
    register_plugin(net_worth_table)
    register_plugin(account_usage_categories)
    register_plugin(income_vs_expense)
    register_plugin(multi_report)


def register_core_configuration_plugins():
    """Entry points that registers all of the core configuration plugins."""
    from gnucash_reports.configuration.base import register_configuration_plugin as _register_configuration_plugin
    from gnucash_reports.configuration.currency import configure as _configure_currency
    from gnucash_reports.configuration.inflation import configure as _configure_inflation
    from gnucash_reports.configuration.tax_tables import configure_tax_tables
    from gnucash_reports.configuration.expense_categories import configure as _configure_expense_categories
    from gnucash_reports.configuration.investment_allocations import configure as _configure_investment_allocations
    from gnucash_reports.configuration.alphavantage import configure as _configure_alpha_vantage

    _register_configuration_plugin(_configure_currency)
    _register_configuration_plugin(_configure_inflation)
    _register_configuration_plugin(configure_tax_tables)
    _register_configuration_plugin(_configure_expense_categories)
    _register_configuration_plugin(_configure_investment_allocations)
    _register_configuration_plugin(_configure_alpha_vantage)
