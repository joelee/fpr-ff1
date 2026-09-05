"""FF1 format-preserving encryption (NIST SP 800-38G)."""

from importlib.metadata import version

from fpr_ff1._exceptions import (
    AlphabetError,
    FF1Error,
    KeyLengthError,
    LengthError,
    RadixError,
    TweakLengthError,
    ValueRangeError,
)
from fpr_ff1._ff1 import FF1

#: The version of the installed ``fpr-ff1`` distribution.  Callers recording
#: which build produced a dataset should capture this alongside their data.
__version__ = version("fpr-ff1")

__all__ = [
    "FF1",
    "AlphabetError",
    "FF1Error",
    "KeyLengthError",
    "LengthError",
    "RadixError",
    "TweakLengthError",
    "ValueRangeError",
    "__version__",
]
