# run-tests-and-lint

## Description
Streamlines the validation process by cleanly executing the project's linter and test suite. It helps maintain code quality by running `make lint` and `make test`, and applying auto-fixes where possible using `ruff`.

## When to Use
- When the user asks to "run tests", "run tests and lint", "check my code", or "verify changes".
- Before finalizing a feature or suggesting a commit.
- When you need to ensure that recent code modifications didn't break existing functionality or violate project formatting rules.

## Instructions
1. **Linting:**
   - Execute `make lint` (which runs `ruff check .` per the Makefile) in the terminal.
   - If there are linting errors, immediately execute `ruff check --fix .` to automatically resolve formatting issues.
   - Manually review and fix any remaining linting errors that could not be auto-fixed.

2. **Testing:**
   - Execute `make test` (which runs `pytest tests/`).
   - If any tests fail, analyze the error tracebacks in the output.
   - Formulate and apply a fix to the relevant source or test files, then re-run `make test` until the suite passes.

3. **Reporting:**
   - Once both commands exit cleanly (Code 0), inform the user that the codebase is fully linted, tested, and ready.