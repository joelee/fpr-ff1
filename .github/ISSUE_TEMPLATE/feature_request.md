name: Feature request
description: An addition or change to the library
labels: ["enhancement"]
body:
  - type: markdown
    attributes:
      value: |
        Note the permanent scope boundaries (see `AGENTS.md`): FF3/FF3-1, key generation, storage,
        derivation, or management, and application-specific defaults or alphabets are out of
        scope and will not be added.
  - type: textarea
    id: problem
    attributes:
      label: What problem does this solve?
      description: The use case, not the solution. A feature that only makes sense for one caller belongs in the caller.
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: Proposed solution
      description: What API change you are proposing, and whether it changes accepted inputs or produced outputs (a major version under this project's policy).
    validations:
      required: true
  - type: checkboxes
    id: scope
    attributes:
      label: Scope check
      options:
        - label: I have checked the scope boundaries above and the open/closed issues for prior discussion.
          required: true