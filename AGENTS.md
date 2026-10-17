# Agent instructions

- Safety first: crisis detection and the crisis response never depend on an LLM. Guardian code fails
  closed: on any error, return the crisis-safe response.
- Never add diagnostic claims or present the assistant as a therapist.
- Conversation content is sensitive personal data (Peru Ley 29733): never log message text, never put
  sensitive content in push notifications.
- Code, comments and docs in English; user-facing copy in neutral Spanish.
- Backend: `cd apps/backend && uv run pytest && uv run ruff check`.
- Behavior changes are test-first (RED → GREEN → refactor).
- Conventional commits; no AI attribution lines.
