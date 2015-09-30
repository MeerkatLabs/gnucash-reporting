import bucket_generation as generator
import key_generator as keys


class BucketCollate(object):

    def __init__(self, bucket_generation, hash_method, store_function):
        self._bucket_generation = bucket_generation
        self._hash_method = hash_method
        self._store_function = store_function

        self._container = self._bucket_generation()

    def reinitialize(self):
        self._container = self._bucket_generation()

    def store_value(self, value):
        key = self._hash_method(value)
        bucket = self._container[key]
        result = self._store_function(bucket, value)
        self._container[key] = result

    @property
    def container(self):
        return self._container


class MonthlyCollate(BucketCollate):

    def __init__(self, start, end, default_value_generator, store_function):
        super(MonthlyCollate, self).__init__(generator.monthly_buckets(start, end, default_value_generator),
                                             keys.monthly,
                                             store_function)

