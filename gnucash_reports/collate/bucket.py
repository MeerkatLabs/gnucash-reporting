from dateutil.rrule import MONTHLY

import bucket_generation as generator
import key_generator as keys


class BucketCollate(object):
    """
    Wrapper that will collate a collection of data based on the hash_method and store_methods provided.
    Also provides functionality for generation of the buckets as well.
    """

    def __init__(self, bucket_generation, hash_method, store_function):
        self._bucket_generation = bucket_generation
        self._hash_method = hash_method
        self._store_function = store_function

        self._container = self._bucket_generation()

    def reinitialize(self):
        self._container = self._bucket_generation()

    def store_value(self, value, key=None):
        if key is None:
            key = self._hash_method(value)
        bucket = self._container[key]
        result = self._store_function(bucket, value)
        self._container[key] = result

    @property
    def container(self):
        return self._container


class PeriodCollate(BucketCollate):
    def __init__(self, start, end, default_value_generator, store_function, frequency=MONTHLY, interval=1):
        super(PeriodCollate, self).__init__(generator.monthly_buckets(start, end,
                                                                      default_value_generator=default_value_generator,
                                                                      frequency=frequency, interval=interval),
                                            keys.period(start, end, frequency=frequency, interval=interval),
                                            store_function)


class CategoryCollate(BucketCollate):
    """
    Collage all of the splits into buckets based on the category that their account is defined in.
    """
    def __init__(self, default_value_generator, store_function):
        super(CategoryCollate, self).__init__(generator.category_buckets(default_value_generator),
                                              keys.category_key_fetcher,
                                              store_function)


class AccountCollate(BucketCollate):
    """
    Collage all of the splits into buckets based on the category that their account is defined in.
    """
    def __init__(self, default_value_generator, store_function):
        super(AccountCollate, self).__init__(generator.category_buckets(default_value_generator),
                                             keys.account_key_fetcher,
                                             store_function)
