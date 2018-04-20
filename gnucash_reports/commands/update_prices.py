import argparse
from datetime import datetime
from yaml import load, Loader
from gnucash_reports.utilities import load_plugins
from gnucash_reports.configuration.alphavantage import get_price_information
from gnucash_reports.configuration import configure_application
from gnucash_reports.configuration import currency
from gnucash_reports.wrapper import initialize
from piecash import Price
from decimal import Decimal


def main():
    load_plugins()

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', dest='configuration', default='core.yaml',
                        help='core configuration details of the application')

    args = parser.parse_args()

    with open(args.configuration) as file_pointer:
        configuration = load(file_pointer, Loader=Loader)
        session = initialize(configuration['gnucash_file'], read_only=False)
        configure_application(configuration.get('global', dict()))

    # print "Value: %s" % (get_price_information('VGSTX'), )

    for commodity in session.commodities:
        if not commodity.quote_flag:
            continue

        if commodity.namespace == 'CURRENCY':
            continue

        quote_date, value = get_price_information(commodity.mnemonic)

        if value is None:
            continue

        print 'Setting value of: %s to %s %s for date: %s' % (commodity.mnemonic, value, currency.get_currency(),
                                                              quote_date)

        Price(currency=currency.get_currency(),
              commodity=commodity,
              date=datetime.combine(quote_date, datetime.max.time()),
              value=Decimal(value),
              source='Finance::Quote',
              type='last')

    session.save()


if __name__ == '__main__':
    main()


