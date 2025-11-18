import collections.abc

import numerical

from ._abstract import Quantity
from ._exceptions import OperationError
from . import _typeface


T = _typeface.TypeVar('T')

class Real:
    """Mixin for adding basic real-valued operator support."""

    def __abs__(self):
        return self

    def __pos__(self):
        return self

    def __neg__(self):
        return self

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return (self < other) and (self == other)

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    def __add__(self, other):
        return self

    def __radd__(self, other):
        return self

    def __sub__(self, other):
        return self

    def __rsub__(self, other):
        return self

    def __mul__(self, other):
        return self

    def __rmul__(self, other):
        return self

    def __truediv__(self, other):
        return self

    def __rtruediv__(self, other):
        return self

    def __floordiv__(self, other):
        return self

    def __rfloordiv__(self, other):
        return self

    def __mod__(self, other):
        return self

    def __rmod__(self, other):
        return self

    def __pow__(self, other):
        return self

    def __rpow__(self, other):
        return self


UserFunction = collections.abc.Callable[..., T]

class NumpyMixin(numerical.mixins.NumpyMixin):
    """Mixin for adding `numpy` support to objects with metadata.

    Notes
    -----
    - This class extends `numerical.mixins.NumpyMixin`. See that class for
      further documentation.
    """

    def _apply_ufunc(self, ufunc, method, *args, **kwargs):
        data = super()._apply_ufunc(ufunc, method, *args, **kwargs)
        f = getattr(ufunc, method)
        types = [type(arg) for arg in args]
        try:
            meta = self._apply_operator_to_metadata(f, *args, **kwargs)
        except OperationError as err:
            raise TypeError(
                f"Cannot apply numpy.{ufunc} to arguments with type(s) {types}"
            ) from err
        if method != 'at':
            return data, meta

    def _apply_function(self, func, types, args, kwargs):
        data = super()._apply_function(func, types, args, kwargs)
        try:
            meta = self._apply_operator_to_metadata(func, *args, **kwargs)
        except OperationError as err:
            raise TypeError(
                f"Cannot apply numpy.{func} to arguments with type(s) {types}"
            ) from err
        return data, meta

    def _apply_operator_to_metadata(self, f, *args, **kwargs):
        """Apply a numpy universal or public function to arguments."""
        keys = {
            k
            for x in args
            if isinstance(x, Quantity)
            for k in x._meta.keys()
        }
        meta = {}
        for key in keys:
            values = [
                x._meta[key]
                if isinstance(x, Quantity) else x
                for x in args
            ]
            errmsg = f"Attribute {key!r} does not support this operation"
            try:
                result = f(*values, **kwargs)
            except TypeError as err:
                if len(values) > 1 and any(v != values[0] for v in values):
                    raise TypeError(errmsg) from err
                else:
                    meta[key] = values[0]
            except OperationError as err:
                raise OperationError(errmsg) from err
            else:
                meta[key] = result
        return meta.copy()

