name: Pull request
description: Submit a change
body:
  - type: markdown
    attributes:
      value: |
        Thank you. Before submitting, please read [`CONTRIBUTING.md`](../CONTRIBUTING.md) —
        especially the vector-provenance rules (never regenerate NIST fixtures, never commit
        self-generated expected values) and the ciphertext-compatibility rule (any change to
        produced output is a major version and needs prior discussion in an issue).
  - type: checkboxes
    id: gate
    attributes:
      label: Quality gate
      options:
        - label: "`just quality` passes locally (format, lint, pyright strict, full suite with the 100% coverage gate)."
          required: true
        - label: "No NIST fixture was regenerated and no self-generated expected value was committed."
          required: true
        - label: "Ciphertext for all currently valid inputs is unchanged, or the change has been discussed in a linked issue."
          required: true
  - type: checkboxes
    id: docs
    attributes:
      label: Documentation
      options:
        - label: "The matching documentation was updated in this change (README, docs/, CHANGELOG `[Unreleased]` as applicable)."
          required: true
  - type: textarea
    id: summary
    attributes:
      label: Summary of changes
      description: What and why, in a few sentences. Reference the issue number if one exists.
    validations:
      required: true