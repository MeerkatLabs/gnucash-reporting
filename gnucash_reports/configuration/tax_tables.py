"""
Attempt to determine federal tax information.
"""
from decimal import Decimal

_tax_tables = dict()


def configure_tax_tables(json_configuration):
    tax_tables = json_configuration.get('taxes')

    # Federal/State Level
    for key, value in tax_tables.iteritems():

        tax_table = dict()
        # Single Married/etc.
        for table_key, table in value.iteritems():

            brackets = []
            for bracket in table:
                row = dict(rate=Decimal(bracket['rate']))
                if 'maximum' in bracket:
                    row['maximum'] = Decimal(bracket['maximum'])
                brackets.append(row)
            tax_table[table_key] = brackets

        _tax_tables[key] = tax_table


def calculate_tax(table_name, table_type, value):
    """
    Calculate the tax based on the table name and the table type.
    :param table_name: this is the name of the table, federal/state.
    :param table_type: this is the type of the table, 'single', 'married', etc.
    :param value: value of income to calculate the tax for.
    :return:
    """

    current_tax = Decimal('0.0')
    previous_maximum = Decimal('0.0')

    table = _tax_tables.get(table_name, dict()).get(table_type, None)
    if table is None:
        raise AttributeError('Unknown table type: %s' % table_type)

    for tax_bracket in table:
        max_value = Decimal('0.0')
        if 'maximum' in tax_bracket:
            if previous_maximum < value:
                max_value = min(value - previous_maximum, tax_bracket['maximum'] - previous_maximum)
            previous_maximum = tax_bracket['maximum']
        else:
            if previous_maximum < value:
                max_value = value - previous_maximum

        current_tax += tax_bracket['rate'] * max_value

    current_tax = current_tax.to_integral_value('ROUND_HALF_UP')

    return current_tax


if __name__ == '__main__':
    assert(calculate_tax('single', Decimal('8225.0')) == Decimal('823.0'))
    assert(calculate_tax('single', Decimal('100000.0')) == Decimal('21071.0'))
    assert(calculate_tax('single', Decimal('500000.0')) == Decimal('154369.0'))
