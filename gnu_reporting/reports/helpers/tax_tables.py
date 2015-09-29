"""
Attempt to determine federal tax information.
"""
from decimal import Decimal

TAX_TABLES = {
    'single': [
        {
            'maximum': Decimal('9225.0'),
            'rate': Decimal('0.1'),
        },
        {
            'maximum': Decimal('37450.0'),
            'rate': Decimal('0.15'),
        },
        {
            'maximum': Decimal('90750.0'),
            'rate': Decimal('0.25'),
        },
        {
            'maximum': Decimal('189300.0'),
            'rate': Decimal('0.28'),
        },
        {
            'maximum': Decimal('411500.0'),
            'rate': Decimal('0.33'),
        },
        {
            'maximum': Decimal('413200.0'),
            'rate': Decimal('0.35'),
        },
        {
            'rate': Decimal('0.396'),
        },
    ],
    'married_jointly': [
        {
            'maximum': Decimal('18450.0'),
            'rate': Decimal('0.1'),
        },
        {
            'maximum': Decimal('74900.0'),
            'rate': Decimal('0.15'),
        },
        {
            'maximum': Decimal('151200.0'),
            'rate': Decimal('0.25'),
        },
        {
            'maximum': Decimal('230450.0'),
            'rate': Decimal('0.28'),
        },
        {
            'maximum': Decimal('411500.0'),
            'rate': Decimal('0.33'),
        },
        {
            'maximum': Decimal('464850.0'),
            'rate': Decimal('0.35'),
        },
        {
            'rate': Decimal('0.396'),
        },
    ],
    'married_separately': [
        {
            'maximum': Decimal('9225.0'),
            'rate': Decimal('0.1'),
        },
        {
            'maximum': Decimal('37450.0'),
            'rate': Decimal('0.15'),
        },
        {
            'maximum': Decimal('75600.0'),
            'rate': Decimal('0.25'),
        },
        {
            'maximum': Decimal('115225.0'),
            'rate': Decimal('0.28'),
        },
        {
            'maximum': Decimal('205750.0'),
            'rate': Decimal('0.33'),
        },
        {
            'maximum': Decimal('232425.0'),
            'rate': Decimal('0.35'),
        },
        {
            'rate': Decimal('0.396')
        },
    ]
}


def calculate_tax(table_type, value):

    current_tax = Decimal('0.0')
    previous_maximum = Decimal('0.0')

    table = TAX_TABLES.get(table_type, None)
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
