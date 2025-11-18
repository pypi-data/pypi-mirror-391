class MetadataTypeError(TypeError):
    """A metadata-related TypeError occurred."""


class MetadataValueError(ValueError):
    """A metadata-related ValueError occurred."""


class OperationError(NotImplementedError):
    """A metadata attribute does not support this operation.
    
    The default behavior when applying an operator to a metadata attribute of
    `~Operand` is to copy the current value if the attribute does not define the
    operation. Custom metadata attributes may raise this exception to indicate
    that attempting to apply the operator is truly an error.
    """

