name: Bug report
description: Something is wrong — wrong output, a crash, or a documentation error
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        **Do not open a public issue for security problems.** A correctness bug that produces
        wrong ciphertext counts as a security issue here — report it privately via
        [GitHub private vulnerability reporting](https://github.com/joelee/fpr-ff1/security/advisories/new).
  - type: input
    id: version
    attributes:
      label: fpr-ff1 version
      description: Output of `python -c "import fpr_ff1; print(fpr_ff1.__version__)"`
      placeholder: "1.0.0"
    validations:
      required: true
  - type: input
    id: environment
    attributes:
      label: Python version and OS
      placeholder: "3.12.13, macOS"
    validations:
      required: true
  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: A minimal reproducer, the exception (type and message), and what you expected instead. Do not paste real plaintext, keys, or production data.
      placeholder: |
        ff1 = FF1(key=..., radix=10, alphabet="0123456789")
        ...
    validations:
      required: true
  - type: checkboxes
    id: conformance
    attributes:
      label: Conformance expectations
      options:
        - label: I have read the README's "Security notes" and understand FF1 provides confidentiality only (no integrity, no error on wrong key/tweak).
          required: true