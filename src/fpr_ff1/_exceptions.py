"""Typed exceptions for the FF1 implementation."""


class FF1Error(Exception):
    """Base for all FF1 errors."""


class KeyLengthError(FF1Error):
    """Key length is not 16, 24, or 32 bytes."""


class RadixError(FF1Error):
    """Radix is outside ``2 <= radix < 2**16``."""


class LengthError(FF1Error):
    """Input length is outside the valid domain for the radix."""


class ValueRangeError(FF1Error):
    """Input data is outside the domain the instance accepts.

    Raised for a numeral outside ``[0, radix)``, and for a character that does
    not appear in the configured alphabet.  Both are faults in the *data* being
    encrypted; malformed *configuration* raises :class:`AlphabetError` instead.
    """


class TweakLengthError(FF1Error):
    """Tweak length is outside the configured bounds."""


class AlphabetError(FF1Error):
    """Alphabet length or uniqueness does not match the radix."""
