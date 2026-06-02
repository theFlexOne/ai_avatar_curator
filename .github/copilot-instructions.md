# GitHub Copilot Instructions

This project follows strict guidelines for AI-assisted development.

- **Primary Context:** Always refer to `instructions.md` for workflow details and `rules.md` for coding standards.
- **Task-Specific:**
    - For data acquisition tasks, focus on robustness, rate-limiting, and error handling.
    - For image processing, use `cv2` and `face_recognition`.
- **Formatting:** Adhere to `ruff` formatting rules.
- **Testing:** Suggest unit tests for filtering logic (e.g., mock images for sharpness checks).
