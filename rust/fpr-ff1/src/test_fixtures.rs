//! Access to the shared JSON fixtures for the crate's tests.
//!
//! The fixtures live in the repository's `tests/vectors/`, beside the Python
//! suite that reads the same files. Cargo packages only files under the
//! crate's own directory, so a published crate carries no fixtures, and
//! copying them in would duplicate the conformance evidence. Instead, as with
//! the Python suite's `FPR_FF1_REQUIRE_*` switches: outside the repository a
//! fixture test announces that it is skipping; with `FPR_FF1_REQUIRE_FIXTURES`
//! set -- as every in-repository run and every CI job sets it -- a missing
//! fixture is a failure, never a silent pass.

use serde_json::Value;

const DIR: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tests/vectors/");

fn required() -> bool {
    std::env::var("FPR_FF1_REQUIRE_FIXTURES").is_ok_and(|v| !v.is_empty() && v != "0")
}

/// Load `tests/vectors/<name>`, or `None` if it is absent and not required.
pub(crate) fn load(name: &str) -> Option<Value> {
    let path = format!("{DIR}{name}");
    match std::fs::read_to_string(&path) {
        Ok(text) => Some(serde_json::from_str(&text).expect("fixtures are valid JSON")),
        Err(e) if required() => {
            panic!("fixture {path} is required (FPR_FF1_REQUIRE_FIXTURES) and unreadable: {e}")
        }
        Err(_) => {
            eprintln!(
                "skipping: fixture {name} is not present (a packaged crate carries no fixtures); \
                 set FPR_FF1_REQUIRE_FIXTURES=1 to make this a failure"
            );
            None
        }
    }
}
