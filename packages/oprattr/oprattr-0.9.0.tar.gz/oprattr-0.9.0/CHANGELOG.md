## NEXT

## v0.9.0

- Update error types raised and messages printed when `mixins.NumpyMixin` processes metadata
- Define the `Attribute` class

## v0.8.0

- Redefine `mixins.NumpyMixin` to extend `numerical.NumpyMixin`
- Redefine `Object` to extend `numerical.Object`
- Improve flexibility of `numpy` functions in `Operand`
- Update types in `__init__.pyi`

## v0.7.0

- Add `oprattr.Object` and `oprattr.Quantity` to the public namespace
- Rename modules that should not be part of the public namespace
- Define the `OperationError` exception class
- Change default behavior when a metadata attribute does not implement an operation

## v0.6.0

- Add `methods` module
- Add `__init__.pyi` type file
- Update metadata error types

## v0.5.0

- Fix `MetadataError` bug
- Improve string representations of `Operand` instances

## v0.4.0

- Replace local `operators` module with equivalent module from `numerical` package
- Redefine equality to always return a single boolean value

## v0.3.0

- Incorporate `numerical` package
- Add `typeface` module

## v0.2.0

- Rename `_types` submodule to `abstract`

## v0.1.0

- Hello world!
