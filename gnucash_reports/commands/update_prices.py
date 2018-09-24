import argparse
import time
from datetime import datetime
from yaml import load, Loader
from gnucash_reports.utilities import load_plugins
from gnucash_reports.configuration.alphavantage import get_price_information
from gnucash_reports.configuration import configure_application
from gnucash_reports.configuration import currency
from gnucash_reports.wrapper import initialize
from piecash import Price
from decimal import Decimal

SLEEP_TIME = 60.0


def main():
    load_plugins()

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', dest='configuration', default='core.yaml',
                        help='core configuration details of the application')

    args = parser.parse_args()

    print('Loading Configuration')

    with open(args.configuration) as file_pointer:
        configuration = load(file_pointer, Loader=Loader)
        session = initialize(configuration['gnucash_file'], read_only=False)
        configure_application(configuration.get('global', dict()))

    # print(f"Value: {get_price_information('VGSTX')}")

    for commodity in session.commodities:
        if not commodity.quote_flag:
            continue

        if commodity.namespace == 'CURRENCY':
            continue

        quote_date, value = get_price_information(commodity.mnemonic)

        if value is not None:
            print(f'Setting value of: {commodity.mnemonic} to {value} {currency.get_currency()} for date: {quote_date}')

            Price(currency=currency.get_currency(),
                  commodity=commodity,
                  date=quote_date,
                  value=Decimal(value),
                  source='Finance::Quote',
                  type='last')

        print(f'Sleeping for: {SLEEP_TIME}')

        time.sleep(SLEEP_TIME)

    session.save()


if __name__ == '__main__':
    main()


