from datetime import date, datetime

def monthly(data_key):
    """
    Returns the bucket that the hash value should be stored into based on the data key that is provided.
    :param data_key: data key value.
    :return: hash key value.
    """
    split_date = datetime.fromtimestamp(data_key.parent.GetDate())
    return date(split_date.year, split_date.month, 1)


