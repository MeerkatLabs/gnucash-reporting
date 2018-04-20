from decimal import Decimal


def split_summation(bucket, value):
    """
    Add value into the contents of the bucket.
    :param bucket: Summation of all splits that have been stored in this bucket.
    :param value: Split object to add to bucket
    :return: new bucket value as a decimal.
    """
    bucket += value.value
    return bucket


def store_credit_debit(bucket, value):
    """
    Store the value of the split into the buckets value.  If the decimal is positive it is considered a credit,
    otherwise it is a debit.
    :param bucket: dictionary containing debits and credits.
    :param value: a decimal or a split
    :return:
    """
    if isinstance(value, Decimal):
        decimal_value = value
    else:
        decimal_value = value.value

    if decimal_value < 0:
        bucket['debit'] += decimal_value
    else:
        bucket['credit'] += decimal_value

    return bucket
