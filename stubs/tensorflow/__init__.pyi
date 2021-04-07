from typing import (
    Any,
    Generic,
    overload,
    Container,
    Iterable,
    Sized,
    SupportsInt,
    SupportsFloat,
    SupportsComplex,
    SupportsBytes,
    SupportsAbs,
    Literal as L,
    TypeVar,
)

from pyre_extensions import TypeVarTuple, Unpack
from numpy import ndarray

Ts = TypeVarTuple("Ts")

A1 = TypeVar("A1")
A2 = TypeVar("A2")
A3 = TypeVar("A3")
A4 = TypeVar("A4")
A5 = TypeVar("A5")

class Variable(Generic[Unpack[Ts]]):
    shape: Tuple[Unpack[Ts]]
    def __init__(
        self,
        initial_value: ndarray[Unpack[Ts]] = ...,
        trainable=...,
        validate_shape=...,
        caching_device=...,
        name=...,
        variable_def=...,
        dtype=...,
        import_scope=...,
        constraint=...,
        synchronization=...,
        aggregation=...,
        shape=...,
    ) -> None: ...

Session: Any = ...
global_variables_initializer: Any = ...
seed: Any = ...

def matmul(
    a,
    b,
    transpose_a=...,
    transpose_b=...,
    adjoint_a=...,
    adjoint_b=...,
    a_is_sparse=...,
    b_is_sparse=...,
    name=...,
) -> Any: ...
