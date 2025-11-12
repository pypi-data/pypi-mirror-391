### Integrated Tests Change Log

This change log records all notable updates to the `integrated_tests` package. Its purpose is to capture changes as we implement them so we can:
- Keep the team up to date in real time
- Consolidate updates into the main documentation in one pass
- Maintain a clear history for auditing and troubleshooting

### Scope
- Changes to test suites (new tests, refactors, removals)
- Test data updates and fixtures
- Test utilities/helpers and shared test infrastructure
- CI test configuration relevant to integrated tests

### How to record changes
Add an entry for every meaningful change as soon as it lands (or when opening the PR). Prefer small, frequent entries over large batched summaries.

- **Date**: YYYY-MM-DD
- **Author**: your name/handle
- **Area**: file(s) or module(s) touched
- **Type**: Add | Change | Fix | Remove | Docs | Infra
- **Description**: concise but specific
- **Rationale**: why this change was needed (if non-obvious)
- **Impact**: behavior, coverage, performance, or developer workflow implications
- **Links**: PR, or related docs

### Format
- Keep entries in reverse chronological order.
- Group under a version heading if applicable; otherwise use an "Unreleased" section at the top.
- Use short, scannable bullets; include links for traceability.

#### Entry template
```text
#### YYYY-MM-DD — Type — Short title
- Author: <name>
- Area: <path/to/test_or_helper.py>
- Description: <what changed>
- Rationale: <why> (optional)
- Impact: <behavior/coverage/infra effects>
- Links: PR #<id>
```

---

### Logs
#### 2025-10-29 - Fix - Test Core
- Author: Pablo
- Area: 
    - modules/integrated_tests/main/acknowledge_manager.py
    - modules/integrated_tests/main/testkit.py
- Description: 
    - Remove unused arguments from key functions (e.g., `issue_type`, `issue_key`).
    - Make sure additional metadata is logged passing the argument to `update_issue_detection()`.
    - Make `issue_identifier` a required argument everywhere possible.
    - Disable pass tests logging
    - Remove hacky workarounds from logging functions that were meant to retrieve the issue identifier from legacy fields.
    - Change hardcoded references to centralized variables.
- Impact: All the scripts where the Integrated Tests were already written, and the ones coming.
- Links: https://github.com/Locaria/locate_2_pulls/pull/7

#### 2025-10-29 - Fix - Generic Tests
- Author: Pablo
- Area: 
    - modules/integrated_tests/generic_tests/data_quality_tests.py
    - modules/integrated_tests/generic_tests/duplicate_tests.py
    - modules/integrated_tests/generic_tests/freshness_tests.py
    - modules/integrated_tests/generic_tests/row_count_tests.py
- Description: 
    - Improve the logs in the different functions by adding more & clearer arguments.
    - Added a `caller_script` argument on the generic tests `__init__` function, so we can have more context in the logs.
    - Streamline the `issue_identifier` definition in each function by dynamically pulling the caller script and the function names (instead of hardcoding them).
    - Created `check_column_completeness()` inside `duplicate_tests.py` to be able to see the completeness in certain columns individually, and not in the whole DataFrame at once.
- Impact: All the scripts where the Integrated Tests were already written, and the ones coming.
- Links: https://github.com/Locaria/locate_2_pulls/pull/7