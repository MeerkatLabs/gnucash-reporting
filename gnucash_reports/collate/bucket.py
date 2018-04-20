"""
Data structures that will be used to sort data into buckets and return the results.  These are essentially helpers for
dictionaries that will execute a hashing function and update the contents of the hash value with the new data.
"""
from dateutil.rrule import MONTHLY

import gnucash_reports.collate.bucket_generation as generator
import gnucash_reports.collate.key_generator as keys


class BucketCollate(object):
    """
    Wrapper that will collate a collection of data based on the hash_method and store_methods provided.
    """

    def __init__(self, bucket_generation, hash_method, store_function):
        """
        Create a bucket sort function.  
        :param bucket_generation: function that creates a list of buckets (dictionary) for data to be stored in.
        :param hash_method: hash method that will be used to convert values into keys if keys are not defined when
        storing values.
        :param store_function: function that defines how the content will be stored in the bucket.
        """
        self._bucket_generation = bucket_generation
        self._hash_method = hash_method
        self._store_function = store_function

        self._container = self._bucket_generation()

    def reinitialize(self):
        """Clear the containers with brand new content."""
        self._container = self._bucket_generation()

    def store_value(self, value, key=None):
        """Store a value ine the container using the store function defined during initialization."""
        if key is None:
            key = self._hash_method(value)
        bucket = self._container[key]
        result = self._store_function(bucket, value)
        self._container[key] = result

    @property
    def container(self):
        """Dictionary that contains the buckets."""
        return self._container


class PeriodCollate(BucketCollate):
    """
    Bucket Collation based on collecting data based on a period of dates.
    """
    def __init__(self, start, end, default_value_generator, store_function, frequency=MONTHLY, interval=1):
        """
        Initializer.
        :param start: start date
        :param end: end date.
        :param default_value_generator: method that will generate the default values for all of the buckets.
        :param store_function: function that will be used to update the contents of the bucket when storing a value.
        :param frequency: how large are the buckets (Monthly, daily, yearly) should be a dateutil.rrule enumeration.
        :param interval: how many frequencies are stored in a bucket.
        """
        super(PeriodCollate, self).__init__(generator.frequency_buckets(start, end,
                                                                        default_value_generator=default_value_generator,
                                                                        frequency=frequency, interval=interval),
                                            keys.period(start, end, frequency=frequency, interval=interval),
                                            store_function)


class CategoryCollate(BucketCollate):
    """
    Collate incoming splits into buckets based on the category that their account is defined in.  Categories are based
    on the configuration values defined in gnucash_reports.configuration.expense_categories
    """

    def __init__(self, default_value_generator, store_function):
        """
        Initializer
        :param default_value_generator: function that creates a default value for each of the buckets.
        :param store_function: function that will be used to update the content of the bucket when storing a split
        value.
        """
        super(CategoryCollate, self).__init__(generator.category_buckets(default_value_generator),
                                              keys.category_key_fetcher,
                                              store_function)


class AccountCollate(BucketCollate):
    """
    Collate all of the splits into buckets based on the last account name in the split's account tree.
    """

    def __init__(self, default_value_generator, store_function):
        """
        Initializer.
        :param default_value_generator: function that creates a default value for each of the buckets.
        :param store_function: function that will be used to update the content of the bucket when storing a split
        value.
        """
        super(AccountCollate, self).__init__(generator.category_buckets(default_value_generator),
                                             keys.account_key_fetcher,
                                             store_function)
