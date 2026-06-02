# GitHub Copilot Instructions

This project follows strict guidelines for AI-assisted development.

- **Primary Context:** Always refer to `progress_diary.md` to understand current state, [instructions.md](../instructions.md) for workflow details, [rules.md](../rules.md) for coding standards, and [ARCHITECTURE.md](../ARCHITECTURE.md) for component boundaries.
- **Commands:** 
  - `make setup`: Set up environment and install dependencies.
  - `make test`: Run pytest suite (`pytest tests/`).
  - `make lint`: Run ruff formatter and linter (`ruff check .`).
  - `make scrape SUBJECT="Target Name"`: Run data acquisition pipeline.
  - `make clean`: Clean cache and environment.
- **Architecture & Structure:** 
  - `src/schemas.py`: Single source of truth using Pydantic models.
  - `src/scrapers/`: Data acquisition (Google, SerpApi).
  - `src/filters/`: Quality control (OpenCV for sharpness, `face_recognition` for ID verification).
  - `src/processors/`: Physical image alterations (crops, standardizations).
  - **Data Immutability:** Files in `data/raw/` are strictly read-only. Processed images write to `data/interim/` or `data/processed/`.
- **Commits:** Group changes into meaningful, atomic commits using Conventional Commits (`feat:`, `fix:`). Do not commit every small change; wait until a feature, fix, or logical task is complete.
- **Task-Specific:**
    - For data acquisition tasks, focus on robustness, asynchronous batch downloading (`aiohttp`), rate-limiting, and error handling.
    - For image processing, use `cv2` and `face_recognition`.
- **Formatting:** Adhere to `ruff` formatting rules, Black's 88-character line length, and Python 3.10+ type hints.
- **Testing:** Suggest and add unit tests using `pytest` for core logic and filtering (e.g., mock images for sharpness checks).

## AI Workflow & Reasoning Guardrails
- **Orchestration First:** If a task spans multiple files, modules, or requires a new phase of implementation, defer coordination to the `Curator` subagent to manage the Audit Loop.
- **Memory & State:** At the start of EVERY response, use the `progress-report` skill to get your bearings on the current project phase and recent milestones, ensuring you do not repeat past mistakes.
- **Plan First (Chain-of-Thought):** Before making edits to the codebase, you MUST write out a step-by-step plan. Explicitly list the files you intend to read, the files you will modify, and how data will flow.
- **Schema-Driven Development:** Whenever starting a new task involving data ingestion or filtering, your FIRST step must be to read `src/schemas.py`. Never use generic dictionaries for data passing; always instantiate or extend the Pydantic models.
- **Image Processing Rules:** `face_recognition` requires RGB images. If reading an image with `cv2.imread()` (defaults to BGR), you MUST convert it to RGB (`cv2.cvtColor(img, cv2.COLOR_BGR2RGB)`).
- **Concrete Test Mocks:** When mocking images for tests, always use standard shapes and types: e.g., `np.zeros((224, 224, 3), dtype=np.uint8)` for RGB, avoiding arbitrary arrays that crash OpenCV. Use the `manage-tmp-files` skill to cleanly generate and remove these transient mock files.
- **Error Recovery:** If a test fails or a command errors out, DO NOT guess the fix. 1. Read the traceback. 2. Output a brief root-cause analysis. 3. Search for context before attempting an edit.
- **Done Criteria & Self-Verification:** Before declaring a task complete, you must run `make lint` and `make test`. Ensure any new scraper or processor has a corresponding test.
