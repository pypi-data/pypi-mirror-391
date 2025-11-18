from pickle import PicklingError


class FailedClass(object):

    def __init__(self, *args, **kwargs):
        self.x = args
        self.y = kwargs

    def __getstate__(self):
        raise PicklingError


class ExampleClass(object):

    def __init__(self, *args, **kwargs):
        self._input_args = args
        self._input_kwargs = kwargs

    def __str__(self):
        return str((self._input_args, self._input_kwargs))

    def __eq__(self, solf):
        if not isinstance(solf, ExampleClass):
            return False
        if not self._input_kwargs == solf._input_kwargs:
            return False
        return self._input_args == solf._input_args


class ExampleSubClass(ExampleClass):
    pass


class OtherClass(object):

    def __init__(self, *args, **kwargs):
        self._input_args = args
        self._input_kwargs = kwargs

    def __str__(self):
        return str((self._input_args, self._input_kwargs))

    def __eq__(self, solf):
        if not isinstance(solf, OtherClass):
            return False
        if not self._input_kwargs == solf._input_kwargs:
            return False
        return self._input_args == solf._input_args


def example_function(*args, **kwargs):
    pass


def example_filter():
    return False
