"""FF1 implementation following NIST SP 800-38G Algorithm 7."""

from __future__ import annotations

import importlib
import operator
from collections.abc import Sequence
from types import ModuleType
from typing import ClassVar, NamedTuple, SupportsIndex, cast

from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    algorithms,
    modes,
)

from fpr_ff1._exceptions import (
    AlphabetError,
    BackendError,
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

    # The tweak length is encoded in four bytes (SP 800-38G Algorithm 7 step
    # 5), so no tweak can exceed FF1._MAX_TWEAK_LEN.  A minimum above it is
    # unsatisfiable; a maximum above it would silently mean the ceiling --
    # a clamp by omission.  Both are rejected (review 00008 MED-03).
    ceiling = FF1._MAX_TWEAK_LEN  # pyright: ignore[reportPrivateUsage]
    if low is not None and low > ceiling:
        raise TweakLengthError(
            f"min_tweak_len {low} above encodable maximum tweak length {ceiling}; "
            "no tweak could satisfy it"
        )
    if high is not None and high > ceiling:
        raise TweakLengthError(
            f"max_tweak_len {high} above encodable maximum tweak length {ceiling}; "
            "bounds are rejected, not clamped"
        )

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
    """Immutable AES configuration shared for the lifetime of one :class:`FF1` instance.

    ``algorithm`` and ``cbc_zero_iv`` are immutable value objects, reused to
    avoid rebuilding them on every PRF call.  No live cipher context is held
    here: a cached encryptor would be shared mutable state, making instances
    unsafe across threads.  Every encryptor -- CBC for the PRF, ECB for the
    step 6.iii expansion -- is created locally to the call that uses it.
    """

    algorithm: algorithms.AES
    cbc_zero_iv: modes.CBC


#: The compiled accelerated backend's module name (plan 00003 E2). The
#: extension lives inside the package namespace (`fpr_ff1._rs`, the
#: standard maturin mixed layout) and is optional: the pure-Python path is
#: the reference and the default, and the package imports fine without it
#: (REQ-19).
_RUST_MODULE = "fpr_ff1._rs"

#: The backend names accepted by :class:`FF1` (REQ-13).
_BACKENDS = ("python", "rust")


def _load_rust_backend() -> ModuleType:
    """Import the compiled backend, raising :class:`BackendError` if absent.

    Called at construction (and unpickling) of a ``backend="rust"``
    instance so the fault surfaces immediately with a typed error, never
    as an opaque ``ImportError`` from inside an encrypt call.  The import
    itself is idempotent and thread-safe (``sys.modules`` caches it).
    """
    try:
        return importlib.import_module(_RUST_MODULE)
    except ImportError as exc:
        raise BackendError(
            "the compiled 'rust' backend is not available in this "
            "installation; the pure-Python backend is the default and "
            "remains available"
        ) from exc


def _rust_ff1(key: bytes, radix: int, x: list[int], tweak: bytes, *, encrypt: bool) -> list[int]:
    """Run one FF1 call on the compiled backend (plan 00003 REQ-13/REQ-18).

    Inputs arrive already validated by :meth:`FF1._prepare`, which runs in
    Python for both backends (plan decision D4) so exception types and
    messages are identical.  The extension is stateless and immutable, so
    per-call lookup through ``sys.modules`` adds no shared mutable state.
    """
    rs = importlib.import_module(_RUST_MODULE)
    fn = rs.encrypt_numerals if encrypt else rs.decrypt_numerals
    return cast("list[int]", fn(key, radix, x, tweak))


class FF1:
    """FF1 format-preserving encryption primitive and string wrapper.

    Thread safety: instances **are** thread-safe. No mutable state is shared
    between calls -- every cipher context is created locally to the call that
    uses it -- so separate calls on one instance may run concurrently and
    will produce exactly the single-threaded results. There is no module-level
    or global state either, so any number of instances may be used
    concurrently.
    """

    # SP 800-38G requires "minlen <= n <= maxlen < 2**32", so the largest
    # admissible length is 2**32 - 1, not 2**32.  Failing closed on the
    # boundary matches the project's stance elsewhere; the excluded value is
    # unconstructable in practice (a 2**32-element list needs tens of GB).
    _MAX_LEN: ClassVar[int] = 2**32 - 1
    # SP 800-38G Algorithm 7 step 5 encodes the tweak length as [t]^4, four
    # big-endian bytes, so 2**32 - 1 is the largest tweak FF1 can express.
    # The spec leaves tweak length otherwise open; this is the encoding's
    # limit, enforced for both backends before any FF1 computation (review
    # 00007 MED-01).
    _MAX_TWEAK_LEN: ClassVar[int] = 2**32 - 1
    _RADIX_MIN: ClassVar[int] = 2
    _RADIX_MAX_EXCLUSIVE: ClassVar[int] = 2**16
    # AES-128/192/256 only.  Named because two entry points validate it --
    # the constructor and __setstate__ -- and they must not drift.
    _KEY_SIZES: ClassVar[frozenset[int]] = frozenset({16, 24, 32})

    def __init__(
        self,
        key: bytes,
        radix: int,
        *,
        alphabet: str | None = None,
        tweak: bytes = b"",
        min_tweak_len: int | None = None,
        max_tweak_len: int | None = None,
        backend: str = "python",
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
            backend: ``"python"`` (the default, and the reference
                implementation) or ``"rust"`` for the opt-in compiled
                backend.  Both produce identical ciphertext; validation
                and exceptions are identical because they run in Python
                for both.

        Raises:
            KeyLengthError: if the key is not bytes-like or has an invalid length.
            RadixError: if the radix is not an integer or is out of range.
            TweakLengthError: if the tweak is not bytes-like or out of bounds.
            AlphabetError: if the alphabet is not a string or is malformed.
            BackendError: if ``backend`` is not a known name, or is
                ``"rust"`` and the compiled extension is not installed.
        """
        # Types are checked before values throughout: a wrong type is the more
        # fundamental fault, and reporting a range error for a float would be
        # actively misleading.
        key = _require_bytes(key, "key", KeyLengthError)
        if len(key) not in self._KEY_SIZES:
            raise KeyLengthError(f"key must be 16, 24, or 32 bytes, got {len(key)}")

        radix = _require_int(radix, "radix", RadixError)
        if radix < self._RADIX_MIN or radix >= self._RADIX_MAX_EXCLUSIVE:
            raise RadixError(
                f"radix must satisfy {self._RADIX_MIN} <= radix < {self._RADIX_MAX_EXCLUSIVE}, "
                f"got {radix!r}"
            )

        # Backend selection (plan 00003 REQ-13): opt-in only, validated like
        # every other configuration parameter -- type first, then value.
        # "rust" fails fast here when the extension is absent, so an
        # unusable instance can never be built (REQ-19).
        if not isinstance(backend, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise BackendError(f"backend must be a str, got {type(backend).__name__}")
        if backend not in _BACKENDS:
            raise BackendError(f"unknown backend {backend!r}; expected 'python' or 'rust'")
        if backend == "rust":
            _load_rust_backend()
        self._backend = backend

        # Retained deliberately: the sole reader is __setstate__, which
        # rebuilds the cipher configuration after unpickling.  Without it the
        # key would have no second reference and instances could not be
        # serialised (review 00003 H3).
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

        # Immutable cipher configuration, reused across calls.  No encryptor
        # is cached: a live context would be shared mutable state, and this
        # instance is safe to share across threads.
        algorithm = algorithms.AES(key)
        self._aes = _Aes(
            algorithm=algorithm,
            cbc_zero_iv=modes.CBC(b"\x00" * 16),
        )

    def __getstate__(self) -> dict[str, object]:
        """Serialise configuration only; cipher objects are rebuilt, never sent.

        Dropping ``_aes`` keeps the pickle payload free of opaque library
        state and makes the payload stable across ``cryptography`` versions.
        The key *is* serialised -- pickling an instance sends key material
        across the process/temp-file/socket boundary at the caller's
        direction; see SECURITY.md.
        """
        state = self.__dict__.copy()
        del state["_aes"]
        return state

    def __setstate__(self, state: dict[str, object]) -> None:
        """Rebuild the cipher configuration from the serialised key."""
        self.__dict__.update(state)
        key = state["_key"]
        # A raise rather than an assert: asserts vanish under ``python -O``,
        # and a non-bytes key here would otherwise surface later as an
        # opaque cryptography error (or worse, from outside the FF1Error
        # hierarchy entirely).
        if not isinstance(key, bytes):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise KeyLengthError(
                f"unpickled FF1 state must carry a bytes key, got {type(key).__name__}"
            )
        # Type is not enough, and for the same reason: a 15-byte bytes key
        # passes the check above and then reaches algorithms.AES, which
        # raises cryptography's own ValueError -- outside FF1Error, so a
        # caller catching the documented hierarchy misses it.  Only the
        # length is re-validated; radix, tweak and alphabet are not, because
        # a pickle is trusted input by policy (SECURITY.md) and this is the
        # one gap that escapes the hierarchy.
        if len(key) not in self._KEY_SIZES:
            raise KeyLengthError(
                f"unpickled FF1 state carries a {len(key)}-byte key; expected 16, 24, or 32"
            )
        # The backend rides in the pickled __dict__ (a plain string).  A
        # pickle from before the backend existed (1.x) has no ``_backend``
        # key and defaults to "python" -- the only backend those versions
        # had.  A hand-crafted state with an unknown backend is rejected
        # rather than silently ignored, mirroring the key check above.
        backend = state.get("_backend", "python")
        if not isinstance(backend, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise BackendError(
                f"unpickled FF1 state must carry a str backend, got {type(backend).__name__}"
            )
        if backend not in _BACKENDS:
            raise BackendError(f"unknown backend {backend!r}; expected 'python' or 'rust'")
        if backend == "rust":
            # Re-validate availability on the far side of the pickle: the
            # receiving process may not have the extension installed.
            _load_rust_backend()
        # Store the validated value.  ``self.__dict__.update(state)`` above
        # already carries ``_backend`` for a 2.x pickle, but a 1.x pickle has
        # no such key and real unpickling never runs ``__init__`` -- without
        # this line every restored 1.x instance raises AttributeError on first
        # use (review 00007 MAJ-01).
        self._backend = backend
        self._aes = _Aes(
            algorithm=algorithms.AES(key),
            cbc_zero_iv=modes.CBC(b"\x00" * 16),
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

    @classmethod
    def _validate_tweak_length(cls, length: int) -> None:
        """Reject a tweak length the four-byte ``[t]^4`` field cannot encode.

        Checked in Python for both backends: without it the reference raised
        ``OverflowError`` (outside ``FF1Error``) from ``_encode_uint`` while
        the compiled core wrapped the length -- a fail-open parity gap.
        """
        if length > cls._MAX_TWEAK_LEN:
            raise TweakLengthError(
                f"tweak length {length} above encodable maximum {cls._MAX_TWEAK_LEN}"
            )

    def _validate_tweak(self, tweak: bytes) -> None:
        # The absolute ceiling first, so an unencodable tweak is reported as
        # such rather than as a configured-bound violation.
        self._validate_tweak_length(len(tweak))
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
                # The rejected value is plaintext data and must not appear in
                # the message: validation exceptions are routinely logged, and
                # SECURITY.md puts "plaintext raised in a message" in scope.
                # The index and the radix stay -- they locate the fault
                # without disclosing it.
                raise ValueRangeError(f"{inout}[{idx}] is out of range for radix {radix}")
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
        # A real Sequence is required, not merely an object with __len__: a
        # mapping or set has no stable iteration order, and a custom object can
        # report any length it likes.  The length is checked before the input
        # is materialised, so an over-long input is rejected without first
        # allocating a copy of it.
        if not isinstance(x, Sequence):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(
                f"{inout} must be a Sequence[int] with a known length, got "
                f"{type(x).__name__}; wrap it with list(...) if it is an iterator"
            )
        declared_length = len(x)
        self._validate_length(declared_length, inout)
        # The tweak is validated before the numerals are walked, so a bad
        # tweak rejects in O(1) rather than after the full coercion pass.
        self._validate_tweak(t)
        numerals = self._coerce_numerals(x, inout)
        # A Sequence's __len__ must be honest: the materialised length is
        # authoritative.  Without this check a lying __len__ passes the
        # minimum-domain gate above while the core encrypts a smaller domain
        # than the package promises to reject.
        if len(numerals) != declared_length:
            raise LengthError(
                f"{inout} declared length {declared_length} but yielded "
                f"{len(numerals)} values; its __len__ is inconsistent"
            )
        # Defensive revalidation before the core (review 00004 MAJ-01): the
        # declared length already passed, so this holds today, but keeping
        # the check here makes _prepare's guarantee local rather than
        # dependent on the coercion path never changing.
        self._validate_length(len(numerals), inout)
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
                # As in _coerce_numerals: the offending character is plaintext
                # data and must not be echoed into a message that callers log.
                # The index locates the fault without disclosing it.
                raise ValueRangeError(f"character at index {idx} is not in the alphabet")
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
        if self._backend == "rust":
            # Validation already ran in _prepare (identical exceptions for
            # both backends, plan decision D4); dispatch to the compiled core.
            return _rust_ff1(self._key, self._radix, numerals, t, encrypt=True)
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
        if self._backend == "rust":
            return _rust_ff1(self._key, self._radix, numerals, t, encrypt=False)
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


#: Inputs at or below this many numerals use the naive spec-reference loops
#: directly: below roughly this size the divide-and-conquer split cannot pay
#: for its recursion (review 00005 measured the crossover well under 64), and
#: the reference loop is the faster implementation.
_D_C_THRESHOLD = 64


def _num_radix_reference(radix: int, numerals: Sequence[int]) -> int:
    """Decode a sequence of numerals as a big-endian base-radix integer.

    The naive digit-at-a-time loop exactly as SP 800-38G specifies NUM_radix.
    Quadratic in the number of numerals, and retained deliberately as the
    line-by-line reference implementation: the subquadratic
    divide-and-conquer path used by :func:`_num_radix` is verified
    bit-identical to this loop across every supported radix by
    ``tests/test_conversion_equivalence.py`` (plan 00003 REQ-03; idea 00001
    r02 MED-01 -- the spec-comparable reference must stay in the module).
    """
    value = 0
    for x in numerals:
        value = value * radix + x
    return value


def _str_radix_reference(value: int, radix: int, length: int) -> list[int]:
    """Encode a non-negative integer as ``length`` big-endian base-radix numerals.

    The naive loop exactly as SP 800-38G specifies STR_radix; see
    :func:`_num_radix_reference` for why the quadratic reference is
    retained. Values ``>= radix ** length`` silently drop their high
    digits; production callers always reduce modulo ``radix ** m`` first
    (step 6.vi), and that contract is pinned by the equivalence tests.
    """
    out = [0] * length
    for i in range(length - 1, -1, -1):
        out[i] = value % radix
        value //= radix
    return out


def _radix_power(radix: int, exponent: int, cache: dict[int, int]) -> int:
    """Return ``radix ** exponent`` through a call-local memo.

    The cache is created per public-helper invocation and passed down the
    recursion. It MUST stay call-local: hoisting it to the instance or
    module level would introduce shared mutable state and silently break
    the thread-safety contract this module documents (plan 00003 REQ-05;
    idea 00001 r02 MED-02). Do not "optimise" this into a module global.
    """
    power = cache.get(exponent)
    if power is None:
        power = radix**exponent
        cache[exponent] = power
    return power


def _num_radix_split(radix: int, numerals: Sequence[int], cache: dict[int, int]) -> int:
    """Divide-and-conquer NUM_radix for inputs above ``_D_C_THRESHOLD``.

    Splits the numeral sequence in half, decodes both halves recursively,
    and combines them as ``high * radix**len(low) + low`` -- one big
    multiply per level instead of one per digit, riding CPython's
    subquadratic big-int multiplication (review 00005 measured O(n^1.2)).
    """
    length = len(numerals)
    if length <= _D_C_THRESHOLD:
        return _num_radix_reference(radix, numerals)
    high_len = length // 2
    high = _num_radix_split(radix, numerals[:high_len], cache)
    low = _num_radix_split(radix, numerals[high_len:], cache)
    return high * _radix_power(radix, length - high_len, cache) + low


def _pow2_exponent(radix: int) -> int | None:
    """Return ``k`` when ``radix`` is ``2 ** k``, else ``None``.

    Exact integer arithmetic only: ``2**k - 1`` has bit length ``k``, so the
    exponent comes from ``bit_length()`` -- never a logarithm (the Bouncy
    Castle bug class this module bans).
    """
    if radix & (radix - 1) == 0:
        return (radix - 1).bit_length()
    return None


def _pow2_chunk_size(k: int) -> int:
    """Smallest numeral count per byte-aligned group for radix ``2 ** k``.

    A group of ``chunk`` numerals occupies ``k * chunk`` bits; the smallest
    ``chunk`` making that a multiple of 8 lets whole groups pass through
    ``int.to_bytes``/``int.from_bytes``. ``k`` is at most 15 (radix < 2**16),
    so 8 always works as the fallback.
    """
    chunk = 8
    for candidate in (1, 2, 4):
        if (k * candidate) % 8 == 0:
            chunk = candidate
            break
    return chunk


def _num_radix_pow2(k: int, numerals: Sequence[int]) -> int:
    """O(n) NUM_radix for power-of-two radices (plan 00003 REQ-02).

    Packs byte-aligned groups of numerals and decodes the whole sequence
    with one ``int.from_bytes`` instead of multiplying per digit. Review
    00005 measured this class of path at 112x end to end for radix 256 at
    n=20,000, bit-exact. Leading zero padding never changes the value.
    """
    chunk_size = _pow2_chunk_size(k)
    bytes_per_chunk = k * chunk_size // 8
    pad = (-len(numerals)) % chunk_size
    padded = [0] * pad + list(numerals)
    packed = bytearray()
    for start in range(0, len(padded), chunk_size):
        acc = 0
        for numeral in padded[start : start + chunk_size]:
            acc = (acc << k) | numeral
        packed += acc.to_bytes(bytes_per_chunk, byteorder="big")
    return int.from_bytes(packed, byteorder="big")


def _str_radix_pow2(value: int, k: int, length: int) -> list[int]:
    """O(n) STR_radix for power-of-two radices; see :func:`_num_radix_pow2`.

    Values ``>= radix ** length`` drop their high digits exactly as the
    reference loop does: ``radix ** length`` is ``2 ** (k * length)`` here,
    so one O(n) mask reproduces the truncation contract bit-for-bit.
    """
    chunk_size = _pow2_chunk_size(k)
    bytes_per_chunk = k * chunk_size // 8
    n_chunks = (length + chunk_size - 1) // chunk_size
    value &= (1 << (k * length)) - 1
    data = value.to_bytes(n_chunks * bytes_per_chunk, byteorder="big")
    digit_mask = (1 << k) - 1
    out: list[int] = []
    for start in range(0, n_chunks * bytes_per_chunk, bytes_per_chunk):
        chunk_int = int.from_bytes(data[start : start + bytes_per_chunk], byteorder="big")
        for shift in range((chunk_size - 1) * k, -1, -k):
            out.append((chunk_int >> shift) & digit_mask)
    # Drop the leading zero padding introduced by the final partial group.
    del out[: n_chunks * chunk_size - length]
    return out


def _num_radix(radix: int, numerals: Sequence[int]) -> int:
    """Decode a sequence of numerals as a big-endian base-radix integer.

    Equivalent to the spec's NUM_radix, bit-identical to
    :func:`_num_radix_reference` (asserted across every supported radix by
    ``tests/test_conversion_equivalence.py``). Inputs at or below
    ``_D_C_THRESHOLD`` numerals use the reference loop directly, so the
    small-input hot path is unchanged; above it, power-of-two radices take
    an O(n) byte-packing path (:func:`_num_radix_pow2`, plan 00003 REQ-02)
    and everything else the subquadratic divide-and-conquer split.
    """
    if len(numerals) <= _D_C_THRESHOLD:
        return _num_radix_reference(radix, numerals)
    k = _pow2_exponent(radix)
    if k is not None:
        return _num_radix_pow2(k, numerals)
    # Call-local cache; see _radix_power for why it must not be shared.
    return _num_radix_split(radix, numerals, {})


def _str_radix_split(value: int, radix: int, length: int, cache: dict[int, int]) -> list[int]:
    """Divide-and-conquer STR_radix for lengths above ``_D_C_THRESHOLD``.

    Splits ``value`` by ``divmod`` against ``radix**len(low_half)`` and
    encodes both halves recursively. A ``value >= radix**length`` drops
    its high digits through the recursion exactly as the reference loop
    does, preserving the truncation contract.
    """
    if length <= _D_C_THRESHOLD:
        return _str_radix_reference(value, radix, length)
    high_len = length // 2
    high, low = divmod(value, _radix_power(radix, length - high_len, cache))
    return _str_radix_split(high, radix, high_len, cache) + _str_radix_split(
        low, radix, length - high_len, cache
    )


def _str_radix(value: int, radix: int, length: int) -> list[int]:
    """Encode a non-negative integer as ``length`` big-endian base-radix numerals.

    Equivalent to the spec's STR_radix, bit-identical to
    :func:`_str_radix_reference`; see :func:`_num_radix` for the
    threshold, power-of-two, and divide-and-conquer dispatch and the
    equivalence guarantees, including the truncation contract for values
    ``>= radix ** length``.
    """
    if length <= _D_C_THRESHOLD:
        return _str_radix_reference(value, radix, length)
    k = _pow2_exponent(radix)
    if k is not None:
        return _str_radix_pow2(value, k, length)
    # Call-local cache; see _radix_power for why it must not be shared.
    return _str_radix_split(value, radix, length, {})


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

    # Loop-invariant moduli, hoisted out of the ten rounds (review 00003
    # M10): step 6.vi reduces modulo radix**m, and m only ever takes the
    # values u and v.
    radix_u = radix**u
    radix_v = radix**v

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
        if len(s_block) < d:
            # The ECB encryptor is created here, local to this call: caching
            # one on the instance would be shared mutable state, and instances
            # are documented as thread-safe.  The cost is zero for d <= 16
            # (this branch never runs) and a few microseconds for the long
            # inputs that do reach it.
            ecb_encryptor = Cipher(aes.algorithm, modes.ECB()).encryptor()
            j = 1
            while len(s_block) < d:
                xored = bytes(p ^ q for p, q in zip(r_block, _encode_uint(j, 16), strict=True))
                s_block += ecb_encryptor.update(xored)
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
            c = (_num_radix(radix, a) + y) % (radix_u if m == u else radix_v)
        else:
            c = (_num_radix(radix, b_side) - y) % (radix_u if m == u else radix_v)

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
