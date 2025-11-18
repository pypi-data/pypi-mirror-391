import numerical

from . import methods
from . import _typeface


T = _typeface.TypeVar('T')

class Attribute(numerical.Object[T], numerical.mixins.NumpyMixin):
    """A metadata attribute with support for numerical operations.

    This class implements all operations required by the real-valued protocol
    (cf. `numerical.Real`). It is meant to serve as a base class from which to
    create metadata attributes for use in subclasses of `~Operand`.

    Notes
    -----
    Although this class implements all real-valued operations, it does not
    assume that its data is real-valued. In fact, it does not even assume that
    its data is numerical.
    """

    def __abs__(self):
        """Called for abs(self)."""
        return self

    def __pos__(self):
        """Called for +self."""
        return self

    def __neg__(self):
        """Called for -self."""
        return self

    def __eq__(self, other):
        """Called for self == other."""
        return equal(self, other)

    def __ne__(self, other):
        """Called for self != other."""
        return not equal(self, other)

    def __lt__(self, other):
        return NotImplemented

    def __le__(self, other):
        return NotImplemented

    def __gt__(self, other):
        return NotImplemented

    def __ge__(self, other):
        return NotImplemented

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


def equal(a, b):
    """Compute a == b between instances of `~Attribute`."""
    if isinstance(a, Attribute) and isinstance(b, Attribute):
        r = a._data == b._data
        try:
            iter(r)
        except TypeError:
            return bool(r)
        return all(r)
    return False

