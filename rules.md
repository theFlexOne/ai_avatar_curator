# Project Rules & Standards

These rules ensure consistency and quality across the AI Avatar Curator repository.

## 1. Development Rules
- **Python Version:** Use Python 3.10 or higher.
- **Formatting:** Use `ruff` for all linting and formatting. Line length: 88 characters (Black style).
- **Typing:** Use type hints for all function signatures.
- **Docstrings:** Use Google-style docstrings for classes and public functions.
- **Dependencies:** Add new packages to `requirements.txt` or `pyproject.toml` immediately.

## 2. Repository Hygiene
- **Commit Messages:** Use Conventional Commits (e.g., `feat:`, `fix:`, `docs:`, `chore:`).
- **Branching:** Use descriptive branch names (e.g., `feature/serpapi-integration`).
- **Secret Management:** Never commit API keys. Use `.env` files and `python-dotenv`.
- **Large Files:** Use `.gitignore` to exclude datasets and model weights.

## 3. Data Integrity
- **Immutability:** Never modify files in `data/raw/` once downloaded. Create processed copies in `data/processed/`.
- **Reproducibility:** Every dataset version should be traceable to a specific search query or source list.
- **Privacy:** If using images of non-public figures, ensure compliance with local data protection laws (e.g., GDPR).

## 4. AI Interaction Rules
- **Verification:** AI agents must verify the existence of a file before attempting to read it.
- **Safety:** Always run shell commands with a timeout and check return codes.
- **Explanation:** Provide a brief summary of changes before applying large edits.
