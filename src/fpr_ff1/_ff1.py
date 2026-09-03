"""FF1 implementation following NIST SP 800-38G Algorithm 7."""

from __future__ import annotations

import operator
from collections.abc import Sequence
from typing import ClassVar, NamedTuple, SupportsIndex, cast

from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    CipherContext,
    algorithms,
    modes,
)

from fpr_ff1._exceptions import (
    AlphabetError,
    FF1Error,
    KeyLengthError,
    LengthError,
    RadixError,
    TweakLengthError,
    ValueRangeError,
)

#: One round's intermediate values, as published in the NIST sample document.
#: Test-only; see :meth:`FF1._encrypt_traced`.
type TraceRecord = dict[str, object]


def _require_int(value: object, name: str, error: type[FF1Error]) -> int:
    """Return ``value`` as an ``int``, rejecting anything not losslessly integral.

    Uses ``operator.index()``, Python's own "this is an integer" protocol:
    ``float`` and ``Decimal`` deliberately do not implement it, while ``int``,
    ``IntEnum`` and NumPy integers do.  Comparison alone is not enough of a
    gate -- ``1.0 < 10`` is ``True``, so a float numeral would otherwise pass
    validation and fail much later with an ``AttributeError`` from outside the
    :class:`FF1Error` hierarchy.

    ``bool`` is rejected explicitly even though it implements ``__index__``:
    silently encrypting ``True`` as ``1`` is the coercion the contract forbids,
    and a sequence of booleans reaching this point is a caller mistake.

    Converting rather than merely checking also normalises NumPy integers to
    Python ``int``, which matters: fixed-width integers would overflow silently
    in the big-integer arithmetic downstream.
    """
    if isinstance(value, bool):
        raise error(f"{name} must be an integer, not bool")
    try:
        # The cast asserts only that __index__ *might* exist; TypeError below
        # is the actual gate.
        return operator.index(cast("SupportsIndex", value))
    except TypeError:
        raise error(f"{name} must be an integer, got {type(value).__name__}") from None


def _validate_tweak_bounds(
    min_tweak_len: int | None, max_tweak_len: int | None
) -> tuple[int | None, int | None]:
    """Type- and sanity-check the configured tweak length bounds.

    These are *configuration* faults, distinct from a tweak that merely
    violates an otherwise valid bound, and they are caught at construction so
    an unusable instance can never be built.

    Raises:
        TweakLengthError: if a bound is not an integer, is negative, or if the
            two bounds are mutually unsatisfiable.
    """
    low = (
        None
        if min_tweak_len is None
        else _require_int(min_tweak_len, "min_tweak_len", TweakLengthError)
    )
    high = (
        None
        if max_tweak_len is None
        else _require_int(max_tweak_len, "max_tweak_len", TweakLengthError)
    )

    for name, bound in (("min_tweak_len", low), ("max_tweak_len", high)):
        if bound is not None and bound < 0:
            # A negative bound is inert rather than harmful, but it silently
            # means "no constraint" -- which is not what the caller asked for.
            raise TweakLengthError(f"{name} must be non-negative, got {bound}")

    if low is not None and high is not None and low > high:
        raise TweakLengthError(
            f"min_tweak_len {low} exceeds max_tweak_len {high}; "
            "no tweak length could satisfy both bounds"
        )

    return low, high


def _require_bytes(value: object, name: str, error: type[FF1Error]) -> bytes:
    """Return ``value`` as ``bytes``, rejecting non-bytes-like input."""
    if not isinstance(value, bytes | bytearray | memoryview):
        raise error(f"{name} must be bytes-like, got {type(value).__name__}")
    # Normalise to immutable bytes: a caller holding the bytearray must not be
    # able to mutate a tweak or key after construction.
    return bytes(cast("bytes | bytearray | memoryview[int]", value))


class _Aes(NamedTuple):
    """AES objects shared for the lifetime of one :class:`FF1` instance.

    ``algorithm`` and ``cbc_zero_iv`` are immutable configuration, reused to
    avoid rebuilding them on every PRF call.  ``ecb_encryptor`` is a live
    context, but ECB carries no chaining state so repeated ``update()`` calls
    are safe.  A CBC *encryptor* is never held here: it would carry chaining
    state between PRF invocations.
    """

    algorithm: algorithms.AES
    cbc_zero_iv: modes.CBC
    ecb_encryptor: CipherContext


class FF1:
    """FF1 format-preserving encryption primitive and string wrapper."""

    # SP 800-38G requires "minlen <= n <= maxlen < 2**32", so the largest
    # admissible length is 2**32 - 1, not 2**32.  Failing closed on the
    # boundary matches the project's stance elsewhere; the excluded value is
    # unconstructable in practice (a 2**32-element list needs tens of GB).
    _MAX_LEN: ClassVar[int] = 2**32 - 1
    _RADIX_MIN: ClassVar[int] = 2
    _RADIX_MAX_EXCLUSIVE: ClassVar[int] = 2**16

    def __init__(
        self,
        key: bytes,
        radix: int,
        *,
        alphabet: str | None = None,
        tweak: bytes = b"",
        min_tweak_len: int | None = None,
        max_tweak_len: int | None = None,
    ) -> None:
        """Create an FF1 instance.

        Args:
            key: AES key; must be 16, 24, or 32 bytes.
            radix: Numeral base, ``2 <= radix < 2**16``.
            alphabet: Optional string of exactly ``radix`` unique characters.
                Required for the string interface.
            tweak: Default tweak used when not provided per call.
            min_tweak_len: Optional inclusive lower bound on tweak length.
            max_tweak_len: Optional inclusive upper bound on tweak length.

        Raises:
            KeyLengthError: if the key is not bytes-like or has an invalid length.
            RadixError: if the radix is not an integer or is out of range.
            TweakLengthError: if the tweak is not bytes-like or out of bounds.
            AlphabetError: if the alphabet is not a string or is malformed.
        """
        # Types are checked before values throughout: a wrong type is the more
        # fundamental fault, and reporting a range error for a float would be
        # actively misleading.
        key = _require_bytes(key, "key", KeyLengthError)
        if len(key) not in {16, 24, 32}:
            raise KeyLengthError(f"key must be 16, 24, or 32 bytes, got {len(key)}")

        radix = _require_int(radix, "radix", RadixError)
        if radix < self._RADIX_MIN or radix >= self._RADIX_MAX_EXCLUSIVE:
            raise RadixError(
                f"radix must satisfy {self._RADIX_MIN} <= radix < {self._RADIX_MAX_EXCLUSIVE}, "
                f"got {radix!r}"
            )

        self._key = key
        self._radix = radix

        # Bounds are validated before the default tweak is checked against
        # them, so an unsatisfiable configuration is reported as such rather
        # than as whichever bound the default tweak happened to violate first.
        self._min_tweak_len, self._max_tweak_len = _validate_tweak_bounds(
            min_tweak_len, max_tweak_len
        )
        tweak = _require_bytes(tweak, "tweak", TweakLengthError)
        self._validate_tweak(tweak)
        self._default_tweak = tweak

        self._alphabet: str | None = None
        self._char_to_index: dict[str, int] | None = None
        self._index_to_char: list[str] | None = None
        if alphabet is not None:
            # Checked at runtime despite the annotation: type hints are not
            # enforced, and a list alphabet silently worked before this guard.
            if not isinstance(alphabet, str):  # pyright: ignore[reportUnnecessaryIsInstance]
                raise AlphabetError(f"alphabet must be a str, got {type(alphabet).__name__}")
            if len(alphabet) != radix:
                raise AlphabetError(f"alphabet length {len(alphabet)} does not match radix {radix}")
            # Uniqueness is by Unicode code point.  Two visually identical but
            # differently-normalised symbols (e.g. precomposed vs decomposed
            # accents) are distinct here; normalisation is the caller's job.
            if len(set(alphabet)) != len(alphabet):
                raise AlphabetError("alphabet contains duplicate characters")
            self._alphabet = alphabet
            self._char_to_index = {ch: i for i, ch in enumerate(alphabet)}
            self._index_to_char = list(alphabet)

        # Every legal radix admits a feasible length: min_length peaks at 20
        # (radix 2), far below _MAX_LEN, so no infeasibility check is needed.
        self._min_length = _min_length(radix)

        # Cipher objects reused across calls.  Do not call finalize() on the
        # ECB encryptor; it must stay alive for the instance's lifetime.
        algorithm = algorithms.AES(key)
        self._aes = _Aes(
            algorithm=algorithm,
            cbc_zero_iv=modes.CBC(b"\x00" * 16),
            ecb_encryptor=Cipher(algorithm, modes.ECB()).encryptor(),
        )

    @property
    def min_length(self) -> int:
        """Minimum permitted input length for this radix."""
        return self._min_length

    @property
    def max_length(self) -> int:
        """Maximum permitted input length for this radix.

        ``2**32 - 1``: SP 800-38G specifies ``maxlen < 2**32``.
        """
        return self._MAX_LEN

    def _validate_tweak(self, tweak: bytes) -> None:
        if self._min_tweak_len is not None and len(tweak) < self._min_tweak_len:
            raise TweakLengthError(f"tweak length {len(tweak)} below minimum {self._min_tweak_len}")
        if self._max_tweak_len is not None and len(tweak) > self._max_tweak_len:
            raise TweakLengthError(f"tweak length {len(tweak)} above maximum {self._max_tweak_len}")

    def _validate_length(self, n: int, inout: str) -> None:
        if n < self._min_length:
            raise LengthError(
                f"{inout} length {n} below minimum {self._min_length} for radix {self._radix}"
            )
        if n > self._MAX_LEN:
            raise LengthError(f"{inout} length {n} above maximum {self._MAX_LEN}")

    def _coerce_numerals(self, x: Sequence[int], inout: str) -> list[int]:
        """Type-check, normalise and range-check numerals in a single pass.

        Returns true Python ``int`` values, so fixed-width integers from other
        numeric libraries cannot reach the big-integer arithmetic downstream
        and overflow silently.
        """
        radix = self._radix
        numerals: list[int] = []
        for idx, value in enumerate(x):
            numeral = _require_int(value, f"{inout}[{idx}]", ValueRangeError)
            if numeral < 0 or numeral >= radix:
                raise ValueRangeError(f"{inout}[{idx}]={numeral!r} out of range for radix {radix}")
            numerals.append(numeral)
        return numerals

    def _prepare(
        self, x: Sequence[int], tweak: bytes | None, inout: str
    ) -> tuple[list[int], bytes]:
        """Validate and normalise the inputs shared by encrypt and decrypt."""
        t = (
            self._default_tweak
            if tweak is None
            else _require_bytes(tweak, "tweak", TweakLengthError)
        )
        # Check the length before materialising the sequence: an over-long
        # input must be rejected without first allocating a copy of it.
        if not hasattr(x, "__len__"):
            raise TypeError(
                f"{inout} must be a Sequence[int] with a known length, got "
                f"{type(x).__name__}; wrap it with list(...) if it is an iterator"
            )
        self._validate_length(len(x), inout)
        numerals = self._coerce_numerals(x, inout)
        self._validate_tweak(t)
        return numerals, t

    def _alphabet_maps(self, numeral_method: str) -> tuple[dict[str, int], list[str]]:
        """Return the alphabet lookup tables, or raise if none was configured."""
        if self._char_to_index is None or self._index_to_char is None:
            raise FF1Error(
                f"alphabet required for string interface; use {numeral_method} "
                "for the numeral interface"
            )
        return self._char_to_index, self._index_to_char

    def _decode_str(self, s: str, char_to_index: dict[str, int]) -> list[int]:
        """Map characters to numerals, rejecting anything outside the alphabet."""
        # Checked at runtime despite the annotation; see _require_int.
        if not isinstance(s, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueRangeError(f"input must be a str, got {type(s).__name__}")
        numerals: list[int] = []
        for idx, ch in enumerate(s):
            value = char_to_index.get(ch)
            if value is None:
                raise ValueRangeError(f"character {ch!r} at index {idx} is not in the alphabet")
            numerals.append(value)
        return numerals

    def encrypt_numerals(self, x: Sequence[int], tweak: bytes | None = None) -> list[int]:
        """Encrypt a sequence of numerals.

        Args:
            x: List of integers in ``[0, radix)``.
            tweak: Tweak bytes; defaults to the instance tweak.

        Returns:
            Encrypted numeral sequence of the same length.

        Raises:
            LengthError: if the input length is outside the valid domain.
            ValueRangeError: if any numeral is outside ``[0, radix)``.
            TweakLengthError: if the tweak is out of bounds.
        """
        numerals, t = self._prepare(x, tweak, "plaintext")
        return _ff1(self._aes, self._radix, numerals, t, encrypt=True)

    def decrypt_numerals(self, x: Sequence[int], tweak: bytes | None = None) -> list[int]:
        """Decrypt a sequence of numerals.

        Args:
            x: List of integers in ``[0, radix)``.
            tweak: Tweak bytes; defaults to the instance tweak.

        Returns:
            Decrypted numeral sequence of the same length.

        Raises:
            LengthError: if the input length is outside the valid domain.
            ValueRangeError: if any numeral is outside ``[0, radix)``.
            TweakLengthError: if the tweak is out of bounds.
        """
        numerals, t = self._prepare(x, tweak, "ciphertext")
        return _ff1(self._aes, self._radix, numerals, t, encrypt=False)

    def _encrypt_traced(
        self, x: Sequence[int], tweak: bytes | None = None
    ) -> tuple[list[int], list[TraceRecord]]:
        """Encrypt, also returning the per-round intermediates.

        Test-only conformance hook, deliberately kept off the public methods:
        the NIST sample document publishes ``P``, ``Q``, ``R``, ``S``, ``y``,
        ``m``, ``c`` and ``C`` for every round, and two compensating bugs can
        agree on the final output while disagreeing here.

        Not exported from the package and not part of the supported API.
        """
        numerals, t = self._prepare(x, tweak, "plaintext")
        trace: list[TraceRecord] = []
        return _ff1(self._aes, self._radix, numerals, t, encrypt=True, _trace=trace), trace

    def encrypt(self, s: str, tweak: bytes | None = None) -> str:
        """Encrypt a string using the configured alphabet.

        Raises:
            FF1Error: if no alphabet was configured at construction.
            ValueRangeError: if a character is absent from the alphabet.
        """
        char_to_index, index_to_char = self._alphabet_maps("encrypt_numerals")
        numerals = self._decode_str(s, char_to_index)
        encrypted = self.encrypt_numerals(numerals, tweak)
        return "".join(index_to_char[i] for i in encrypted)

    def decrypt(self, s: str, tweak: bytes | None = None) -> str:
        """Decrypt a string using the configured alphabet.

        Raises:
            FF1Error: if no alphabet was configured at construction.
            ValueRangeError: if a character is absent from the alphabet.
        """
        char_to_index, index_to_char = self._alphabet_maps("decrypt_numerals")
        numerals = self._decode_str(s, char_to_index)
        decrypted = self.decrypt_numerals(numerals, tweak)
        return "".join(index_to_char[i] for i in decrypted)


_MIN_DOMAIN = 1_000_000


def _min_length(radix: int) -> int:
    """Return the smallest n with radix**n >= 1_000_000."""
    n = 1
    value = radix
    while value < _MIN_DOMAIN:
        value *= radix
        n += 1
    return n


def _num_radix(radix: int, numerals: Sequence[int]) -> int:
    """Decode a sequence of numerals as a big-endian base-radix integer."""
    value = 0
    for x in numerals:
        value = value * radix + x
    return value


def _str_radix(value: int, radix: int, length: int) -> list[int]:
    """Encode a non-negative integer as ``length`` big-endian base-radix numerals."""
    out = [0] * length
    for i in range(length - 1, -1, -1):
        out[i] = value % radix
        value //= radix
    return out


def _prf(aes: _Aes, data: bytes) -> bytes:
    """SP 800-38G Algorithm 6 (PRF): CBC-MAC with a zero IV.

    Invoked from Algorithm 7 step 6.ii as ``PRF(P || Q)``.
    """
    # data is already 16-byte aligned by callers.  A fresh encryptor per call
    # is required: CBC chaining state must never persist between PRF calls.
    encryptor = Cipher(aes.algorithm, aes.cbc_zero_iv).encryptor()
    result = encryptor.update(data) + encryptor.finalize()
    return result[-16:]


def _ff1(
    aes: _Aes,
    radix: int,
    x: list[int],
    tweak: bytes,
    *,
    encrypt: bool,
    _trace: list[TraceRecord] | None = None,
) -> list[int]:
    """SP 800-38G Algorithm 7 core."""
    n = len(x)

    # Step 1: u = floor(n/2), v = n - u
    u = n // 2
    v = n - u

    # Step 2: A = X[1..u], B = X[u+1..n]
    a = x[:u]
    b_side = x[u:]

    # Step 3: b = ceil(ceil(v * log2(radix)) / 8) -- derived from v, not u.
    # The bit length uses exact integer arithmetic; never math.log2.
    b = ((radix**v - 1).bit_length() + 7) // 8

    # Step 4: d = 4 * ceil(b/4) + 4
    d = 4 * ((b + 3) // 4) + 4

    t = len(tweak)
    pad = (-(t + b + 1)) % 16

    # Step 5: P is loop-invariant, so it is built once here rather than
    # rebuilt on each of the ten rounds.
    p_block = (
        bytes([1, 2, 1])
        + _encode_uint(radix, 3)
        + bytes([10, u % 256])
        + _encode_uint(n, 4)
        + _encode_uint(t, 4)
    )

    rounds = range(10) if encrypt else range(9, -1, -1)

    for i in rounds:
        # Step 6.i: Q = T || [0]^pad || [i]^1 || [NUM_radix(B)]^b
        # (decrypt builds Q from A instead of B)
        if encrypt:
            q_block = (
                tweak + bytes([0]) * pad + bytes([i]) + _encode_uint(_num_radix(radix, b_side), b)
            )
        else:
            q_block = tweak + bytes([0]) * pad + bytes([i]) + _encode_uint(_num_radix(radix, a), b)

        # Step 6.ii: R = PRF(P || Q)
        r_block = _prf(aes, p_block + q_block)

        # Step 6.iii: S is the first d bytes of
        #   R || CIPH_K(R XOR [1]^16) || CIPH_K(R XOR [2]^16) || ...
        # Each expansion block is a SINGLE forward-cipher block over R XOR the
        # 16-byte encoding of j.  It is not a PRF, and j is not concatenated
        # onto R -- both mistakes produce a non-16-byte-aligned input and are
        # invisible to the NIST samples, none of which reach d > 16.
        s_block = r_block
        j = 1
        while len(s_block) < d:
            xored = bytes(p ^ q for p, q in zip(r_block, _encode_uint(j, 16), strict=True))
            s_block += aes.ecb_encryptor.update(xored)
            j += 1
        # Truncate to d BYTES, not d bits.
        s_block = s_block[:d]

        # Step 6.iv: y = NUM(S)
        y = int.from_bytes(s_block, byteorder="big")

        # Step 6.v: parity rule is identical for encrypt and decrypt
        m = u if i % 2 == 0 else v

        # Step 6.vi: c = (NUM_radix(A) + y) mod radix**m  (decrypt subtracts
        # y from NUM_radix(B) instead)
        if encrypt:
            c = (_num_radix(radix, a) + y) % (radix**m)
        else:
            c = (_num_radix(radix, b_side) - y) % (radix**m)

        # Step 6.vii: C = STR^m_radix(c)
        c_block = _str_radix(c, radix, m)

        if _trace is not None:
            _trace.append(
                {
                    "i": i,
                    "u": u,
                    "v": v,
                    "b": b,
                    "d": d,
                    "P": list(p_block),
                    "Q": list(q_block),
                    "R": list(r_block),
                    "S": list(s_block),
                    "y": y,
                    "m": m,
                    "c": c,
                    "C": list(c_block),
                    "A_before": list(a),
                    "B_before": list(b_side),
                }
            )

        # Steps 6.viii and 6.ix: A = B, B = C  (decrypt assigns B = A, A = C)
        if encrypt:
            a = b_side
            b_side = c_block
        else:
            b_side = a
            a = c_block

    # Step 7: return A || B
    return a + b_side


def _encode_uint(value: int, length: int) -> bytes:
    """Encode a non-negative integer as a big-endian ``length``-byte string.

    Raises ``OverflowError`` if the value does not fit, which is deliberate:
    silently truncating would corrupt Q and produce non-conformant ciphertext.
    """
    return value.to_bytes(length, byteorder="big")
