from typing import Callable, TypeAlias, no_type_check

from typing_extensions import TypeVar

# Type variables
T = TypeVar("T")
# Complex type for _Complex in C
Complex: TypeAlias = complex

# Callback function types
CallbackFunc: TypeAlias = Callable[..., int]
VoidCallbackFunc: TypeAlias = Callable[..., None]


class CData:
    """Base class for cffi C-compatible data structures.

    This is an abstract base class that serves as the foundation for all C-compatible
    data types in the chc2c package. It represents memory structures that are passed
    between Python and C code via cffi.
    """


class Ptr[T](CData):
    """Generic pointer type that supports arithmetic operations (+, -, []).

    A typed pointer type that wraps cffi pointers, enabling safe memory access and
    pointer arithmetic in Python. The generic type T represents the type of data
    being pointed to. Supports addition/subtraction of integers (pointer arithmetic)
    and index access to elements in the memory block.

    Type parameters:
        T: The type of the elements being pointed to.

    Example:
        ptr: Ptr[float64] = ...  # Pointer to float64 values
        val = ptr[0]  # Access first element
        next_ptr = ptr + 1  # Move pointer to next element

    """

    @no_type_check
    def __add__(self, rhs: int) -> "Ptr": ...

    @no_type_check
    def __radd__(self, lhs: int) -> "Ptr": ...

    @no_type_check
    def __sub__(self, rhs: int) -> "Ptr": ...

    @no_type_check
    def __getitem__(self, index: int) -> T: ...


class CArray[T](Ptr[T]):
    """Array type derived from Ptr, with length information.

    An extension of Ptr that represents an array with known length. This type provides
    a Pythonic interface to C arrays by implementing the __len__ method, making it
    compatible with Python's len() function.

    Type parameters:
        T: The type of the elements in the array.

    Note:
        The actual length information is typically stored in the C data structure
        and made available through the managing class (e.g., Atoms, Shells).

    """

    @no_type_check
    def __len__(self) -> int: ...
