from datetime import datetime

_today = datetime.today()


def configure(json_configuration):
    global _today

    date = json_configuration.get('date', None)

    if date:
        _today = datetime.strptime(date, '%Y-%m-%d')


def get_today():
    return _today