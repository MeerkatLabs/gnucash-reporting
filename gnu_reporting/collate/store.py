from gnu_reporting.wrapper import get_decimal


def split_summation(bucket, value):
    """
    sum the new value to the value in the bucket.
    :param bucket: Decimal object
    :param value: Split object
    :return: new bucket value
    """
    bucket += get_decimal(value.GetAmount())
    return bucket


def store_credit_debit(bucket, value):
    decimal_value = get_decimal(value.GetAmount())

    if decimal_value < 0:
        bucket['debit'] += decimal_value
    else:
        bucket['credit'] += decimal_value

    return bucket
