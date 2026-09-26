//! The public FF1 type (plan 00009 STEP-06).

use std::collections::HashMap;

use crate::engine;
use crate::error::Error;
use crate::validate::{self, Operand, MAX_LEN};

/// An FF1 cipher: a key, a radix and optional configuration, validated once.
///
/// Every input is validated before any computation, with the same rules,
/// order and messages as the `fpr-ff1` Python package; see [`Error`].
///
/// An instance holds only its configuration. No cipher context is cached:
/// each call builds its own AES key schedule, so an instance may be shared
/// freely between threads.
#[derive(Clone)]
pub struct FF1 {
    key: Vec<u8>,
    radix: u32,
    min_length: usize,
    default_tweak: Vec<u8>,
    min_tweak_len: Option<usize>,
    max_tweak_len: Option<usize>,
    alphabet: Option<Alphabet>,
}

// The key is deliberately left out of Debug output: it is secret material.
impl std::fmt::Debug for FF1 {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("FF1")
            .field("radix", &self.radix)
            .field("min_length", &self.min_length)
            .field("min_tweak_len", &self.min_tweak_len)
            .field("max_tweak_len", &self.max_tweak_len)
            .field("has_alphabet", &self.alphabet.is_some())
            .finish_non_exhaustive()
    }
}

/// The characters for the string interface, one per numeral.
#[derive(Clone)]
struct Alphabet {
    chars: Vec<char>,
    index: HashMap<char, u16>,
}

/// Configures an [`FF1`]; obtained from [`FF1::builder`].
#[derive(Clone)]
#[must_use = "a builder does nothing until .build() is called"]
pub struct Builder<'a> {
    key: &'a [u8],
    radix: u32,
    alphabet: Option<&'a str>,
    tweak: &'a [u8],
    min_tweak_len: Option<usize>,
    max_tweak_len: Option<usize>,
}

impl<'a> Builder<'a> {
    /// Enable the string interface: exactly `radix` distinct characters, the
    /// character at position `i` standing for numeral `i`.
    pub fn alphabet(mut self, alphabet: &'a str) -> Self {
        self.alphabet = Some(alphabet);
        self
    }

    /// The tweak used when a call passes `None`. Defaults to empty.
    pub fn tweak(mut self, tweak: &'a [u8]) -> Self {
        self.tweak = tweak;
        self
    }

    /// Inclusive minimum tweak length, checked on every tweak.
    pub fn min_tweak_len(mut self, len: usize) -> Self {
        self.min_tweak_len = Some(len);
        self
    }

    /// Inclusive maximum tweak length, checked on every tweak. `0` is literal
    /// and admits only an empty tweak; leave it unset for no maximum.
    pub fn max_tweak_len(mut self, len: usize) -> Self {
        self.max_tweak_len = Some(len);
        self
    }

    /// Validate the configuration and build the cipher.
    ///
    /// Checks run in the Python package's order -- key, radix, tweak
    /// bounds, default tweak, alphabet -- so a configuration with several
    /// faults reports the same one in both.
    pub fn build(self) -> Result<FF1, Error> {
        validate::key(self.key)?;
        validate::radix(self.radix)?;
        validate::tweak_bounds(self.min_tweak_len, self.max_tweak_len)?;
        validate::tweak(self.tweak.len(), self.min_tweak_len, self.max_tweak_len)?;
        let alphabet = match self.alphabet {
            None => None,
            Some(text) => {
                let chars = validate::alphabet(text, self.radix)?;
                // radix < 2**16, so every position fits a u16.
                let index = chars
                    .iter()
                    .enumerate()
                    .map(|(i, &c)| (c, u16::try_from(i).expect("position < radix < 2**16")))
                    .collect();
                Some(Alphabet { chars, index })
            }
        };
        Ok(FF1 {
            key: self.key.to_vec(),
            radix: self.radix,
            min_length: validate::min_length(self.radix),
            default_tweak: self.tweak.to_vec(),
            min_tweak_len: self.min_tweak_len,
            max_tweak_len: self.max_tweak_len,
            alphabet,
        })
    }
}

impl FF1 {
    /// An FF1 cipher with no alphabet, an empty default tweak and no tweak
    /// bounds. Equivalent to `FF1::builder(key, radix).build()`.
    ///
    /// `key` must be 16, 24 or 32 bytes; `radix` must satisfy
    /// `2 <= radix < 2**16`.
    pub fn new(key: &[u8], radix: u32) -> Result<FF1, Error> {
        FF1::builder(key, radix).build()
    }

    /// Start configuring an FF1 cipher with an alphabet, a default tweak or
    /// tweak-length bounds.
    pub fn builder(key: &[u8], radix: u32) -> Builder<'_> {
        Builder {
            key,
            radix,
            alphabet: None,
            tweak: &[],
            min_tweak_len: None,
            max_tweak_len: None,
        }
    }

    /// Encrypt a numeral sequence (SP 800-38G Algorithm 7). Each numeral must
    /// be less than the radix. `tweak` of `None` uses the default tweak.
    pub fn encrypt_numerals(&self, x: &[u16], tweak: Option<&[u8]>) -> Result<Vec<u16>, Error> {
        self.run(x, tweak, Operand::Plaintext)
    }

    /// Decrypt a numeral sequence (SP 800-38G Algorithm 8). Each numeral must
    /// be less than the radix. `tweak` of `None` uses the default tweak.
    pub fn decrypt_numerals(&self, x: &[u16], tweak: Option<&[u8]>) -> Result<Vec<u16>, Error> {
        self.run(x, tweak, Operand::Ciphertext)
    }

    /// Encrypt a string over the configured alphabet.
    pub fn encrypt(&self, s: &str, tweak: Option<&[u8]>) -> Result<String, Error> {
        let alphabet = self
            .alphabet
            .as_ref()
            .ok_or_else(|| validate::alphabet_required("encrypt_numerals"))?;
        let numerals = validate::decode(s, &alphabet.index)?;
        let out = self.encrypt_numerals(&numerals, tweak)?;
        Ok(alphabet.encode(&out))
    }

    /// Decrypt a string over the configured alphabet.
    pub fn decrypt(&self, s: &str, tweak: Option<&[u8]>) -> Result<String, Error> {
        let alphabet = self
            .alphabet
            .as_ref()
            .ok_or_else(|| validate::alphabet_required("decrypt_numerals"))?;
        let numerals = validate::decode(s, &alphabet.index)?;
        let out = self.decrypt_numerals(&numerals, tweak)?;
        Ok(alphabet.encode(&out))
    }

    /// The shortest input accepted for this radix: the smallest `n` with
    /// `radix**n >= 1_000_000` (6 for radix 10, 20 for radix 2).
    pub fn min_length(&self) -> usize {
        self.min_length
    }

    /// The longest input accepted: `2**32 - 1`, since SP 800-38G requires
    /// `maxlen < 2**32`.
    pub fn max_length(&self) -> u64 {
        MAX_LEN
    }

    /// Validate in the Python package's order -- length, then tweak, then
    /// each numeral -- and run the core.
    fn run(&self, x: &[u16], tweak: Option<&[u8]>, operand: Operand) -> Result<Vec<u16>, Error> {
        let tweak = tweak.unwrap_or(&self.default_tweak);
        validate::length(x.len(), self.min_length, self.radix, operand)?;
        validate::tweak(tweak.len(), self.min_tweak_len, self.max_tweak_len)?;
        validate::numerals(x, self.radix, operand)?;
        let encrypt = operand == Operand::Plaintext;
        // Every condition the core can refuse -- key size, an empty input, a
        // length or tweak that does not fit four bytes -- was rejected above,
        // so a core error here would be a defect in this crate, not in the
        // caller's input.
        Ok(engine::ff1(&self.key, self.radix, x, tweak, encrypt)
            .expect("inputs were validated; the FF1 core cannot fail on them"))
    }
}

impl Alphabet {
    fn encode(&self, numerals: &[u16]) -> String {
        numerals
            .iter()
            .map(|&v| self.chars[usize::from(v)])
            .collect()
    }
}
