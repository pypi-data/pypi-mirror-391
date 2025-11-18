import numpy

from . import _abstract
from . import methods
from . import mixins
from ._operations import equality
from . import _typeface


T = _typeface.TypeVar('T')

class Operand(_abstract.Object[T], mixins.NumpyMixin):
    """A concrete implementation of a real-valued object."""

    __abs__ = methods.__abs__
    __pos__ = methods.__pos__
    __neg__ = methods.__neg__

    __eq__ = methods.__eq__
    __ne__ = methods.__ne__
    __lt__ = methods.__lt__
    __le__ = methods.__le__
    __gt__ = methods.__gt__
    __ge__ = methods.__ge__

    __add__ = methods.__add__
    __radd__ = methods.__radd__
    __sub__ = methods.__sub__
    __rsub__ = methods.__rsub__
    __mul__ = methods.__mul__
    __rmul__ = methods.__rmul__
    __truediv__ = methods.__truediv__
    __rtruediv__ = methods.__rtruediv__
    __floordiv__ = methods.__floordiv__
    __rfloordiv__ = methods.__rfloordiv__
    __mod__ = methods.__mod__
    __rmod__ = methods.__rmod__
    __pow__ = methods.__pow__
    __rpow__ = methods.__rpow__

    def __array__(self, *args, **kwargs):
        """Called for numpy.array(self)."""
        return numpy.array(self._data, *args, **kwargs)

    def _apply_ufunc(self, ufunc, method, *args, **kwargs):
        if ufunc in (numpy.equal, numpy.not_equal):
            # NOTE: We are probably here because the left operand is a
            # `numpy.ndarray`, which would otherwise take control and return the
            # pure `numpy` result.
            f = getattr(ufunc, method)
            return equality(f, *args)
        data, meta = super()._apply_ufunc(ufunc, method, *args, **kwargs)
        return self._from_numpy(data, **meta)

    def _apply_function(self, func, types, args, kwargs):
        data, meta = super()._apply_function(func, types, args, kwargs)
        if data is NotImplemented:
            return data
        return self._from_numpy(data, **meta)

    def _get_numpy_array(self):
        return numpy.array(self._data)

    def _from_numpy(self, data, **meta):
        """Create a new instance after applying a numpy function."""
        if isinstance(data, (list, tuple)):
            r = [self._factory(array, **meta) for array in data]
            if isinstance(data, tuple):
                return tuple(r)
            return r
        return self._factory(data, **meta)

    def _factory(self, data, **meta):
        """Create a new instance from data and metadata.

        The default implementation uses the standard `__new__` constructor.
        Subclasses may overload this method to use a different constructor
        (e.g., a module-defined factory function).
        """
        return type(self)(data, **meta)


@Operand.implementation(numpy.array_equal)
def array_equal(
    x: numpy.typing.ArrayLike,
    y: numpy.typing.ArrayLike,
    **kwargs
) -> bool:
    """Called for numpy.array_equal(x, y)"""
    return numpy.array_equal(numpy.array(x), numpy.array(y), **kwargs)


