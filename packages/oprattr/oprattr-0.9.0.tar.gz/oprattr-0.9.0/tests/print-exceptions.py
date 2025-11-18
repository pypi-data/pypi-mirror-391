"""
This script generates and echos exceptions related to operations on instances of
the `Operand` class. It is meant as a supplement to rigorous tests.
"""

import numerical
import oprattr

x = oprattr.Operand(1, name='A')
y = oprattr.Operand(2, name='B')

cases = (
    (numerical.operators.lt, x, y),
    (numerical.operators.lt, x, 2),
    (numerical.operators.lt, 2, x),
    (numerical.operators.add, x, y),
    (numerical.operators.add, x, 2),
    (numerical.operators.add, 2, y),
    (numerical.operators.abs, x),
    (numerical.operators.mul, x, 'y'),
    (numerical.operators.mul, 'x', y),
    (numerical.operators.pow, x, 2)
)

successes = 0
failures = 0
for f, *args in cases:
    try:
        f(*args)
    except Exception as exc:
        print(f"Caught {type(exc).__qualname__}: {exc}")
        successes += 1
    else:
        strargs = ', '.join(str(arg) for arg in args)
        print(f"Calling {f} on {strargs} did not raise an exception")
        failures += 1
    print()

print(f"Successes: {successes}")
print(f"Failures: {failures}")

