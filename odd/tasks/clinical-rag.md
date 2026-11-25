# Feature: clinical-rag

Objective: ground the companion's replies in licensed lay material (WHO "Doing What Matters", Spanish edition) with hybrid retrieval on PostgreSQL + pgvector, cited sources, and a measured retrieval evaluation; deliver it as a working app (backend, database, mobile).
Branch: `feat/clinical-rag` · Delivery: ask-on-risk (work-unit commits on the branch; push and PR are the user's decision) · Runner: `cd apps/backend && uv run pytest && uv run ruff check`; mobile `flutter test` (Flutter is not installed on this machine yet).
Locator: `odd/tasks/clinical-rag.md` · Engram mirror: `odd/clinical-rag/tasks`

## Specs

- S1 Corpus. Source: "En tiempos de estrés, haz lo que importa: una guía ilustrada" (WHO 2020, ISBN 978-92-4-000956-1, CC BY-NC-SA 3.0 IGO), downloaded from `https://www.who.int/docs/default-source/mental-health/sh-2020-spa-3-web.pdf` with user approval. A fetch script pins the file's SHA-256; the raw PDF stays out of git. Extraction with pypdf, cleaned of page numbers, running headers and illustration noise; chunks follow the book structure (parts, pages, the five summary tools) and carry `source_id`, `part`, `pages`, `audience=lay`, `content_type`, `licence` and attribution metadata. Processed chunks are committed as JSONL with a NOTICE carrying the WHO citation and licence. Front matter (licence, acknowledgements, reviewers) is not indexed.
- S2 Storage and retrieval. PostgreSQL + pgvector through Docker Compose. Chunks table with a Spanish `tsvector`; one embedding table per embedding model with an HNSW cosine index. Three retrieval modes: dense, lexical (full-text, `spanish` config) and hybrid (Reciprocal Rank Fusion). Retrieval always filters `audience = 'lay'` and excludes `content_type in ('dosing', 'diagnostic')`.
- S3 Embeddings run locally (fastembed, ONNX), never through a third-party API: every user message turned into a query embedding is sensitive personal data (Ley 29733). Candidates: `intfloat/multilingual-e5-large`, `jinaai/jina-embeddings-v2-base-es`, `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. The default is chosen by the evaluation (S5), not by assumption.
- S4 Grounded replies. Flow stays: guardian on input → crisis response without model or retrieval → retrieval → companion → guardian on output. Retrieved chunks go into the prompt as reference material with ids; the model cites `[id]`; the backend keeps only citations of chunks actually retrieved, removes citation markers from the text and returns `sources` (title, part, pages, attribution) with the reply. If retrieval fails or is not configured, the companion answers without references (degraded, never an error). Crisis and referral resources never come from RAG. Message text and queries are never logged.
- S5 Evaluation. A question set in Peruvian colloquial Spanish, each labelled with the relevant book pages (relevance is by page overlap, so it survives re-chunking). Metrics: recall@1/3/5/10 and MRR, for every embedding model × mode (dense, lexical, hybrid), against the real Postgres store. A CLI writes a Markdown report under `apps/backend/eval/reports/`. The questions were written by the assistant and not reviewed by clinicians: a stated limitation.
- S6 Runnable app. Backend container and Compose service (database, one-shot ingestion, API) with health checks; settings by environment; docs on how to run everything locally.
- S7 Mobile. The chat shows the sources under a reply that used them, with the WHO attribution.
- S8 Quality gates. Unit tests with fakes (no network, no model downloads); integration tests against Postgres, skipped unless `PUENTE_TEST_DATABASE_URL` is set; GitHub Actions runs lint and both test layers with a pgvector service.

Assumption (L1 "con todo lo necesario"): "complete app" is read as this RAG feature delivered end to end (S1–S8). Auth, persistence of conversations, mood tracking and the LLM judge remain later features from `mvp-foundation.md`.

## Tasks

| ID | Specs | Route | Status | Commit / evidence |
|----|-------|-------|--------|-------------------|
| T1 | S1 | inline | done | `eccbaf9`. RED: collection error, then the ligature test failed; GREEN: 11 passed. Review assess: medium, under_budget |
| T2 | S2, S8 | inline | done | `d718ac9`. RED: 2 of 10 integration tests failed (double stemming in `to_tsquery`; fixed with a `::tsquery` cast); GREEN: 26 passed against Postgres |
| T3 | S3 | inline | done | `d718ac9`. RED: 3 of 8 failed (e5 prefixes missing in fastembed); GREEN: 8 passed. All 3 models ingested (58 chunks each). Review assess: medium, under_budget (2,274 lines incl. lockfile) |
| T4 | S4 | inline | done (review pending) | `a27961e`. RED: collection errors, then 2 of 3 readiness tests failed; GREEN: 161 passed (11 skipped) without DB, 172 with DB. Risk: item 2 (guarded flow), escalated; review due |
| T5 | S5 | inline | pending | |
| T6 | S6 | inline | pending | |
| T7 | S7 | pending decision (Flutter missing) | pending | |
| T8 | S8 | inline | pending | |

Route evidence: one dependent chain (corpus → store → retrieval → companion → eval), no independent parallel units, so the parent writes inline (no Writer trigger).

## Log

- L1 (2026-11-24, user, verbatim): "todavía no existe, empecemos con el RAG de Puente, revisa mi repsositorioa de github, y ahi veras y busca en esta computadora"
- L2 (2026-11-24, user, verbatim, approving the proposed plan and the PDF download): "SI realizaloa, HASTA HACERLO UN APP FUNCIOnal completa, con todo lo necessario buenas practicas y de mas, avisame aucnodo etse listo"
- L3 Evidence: the repo had no RAG code (only `docs/research`). The research notes recommend pgvector HNSW + Spanish tsvector + RRF, choosing embeddings by a local eval, filtering `audience=lay`, validating `[chunk_id]` citations and never routing crisis resources through RAG. WHO DWM Spanish is the only fully cleared lay source; the PAHO adaptation says "Todos los derechos reservados" and is excluded.
- L4 Evidence: the PDF has 132 pages and ~12,800 words, illustrated with speech bubbles. pypdf extracts it better than pdftotext. BGE-M3 is not in fastembed 0.9.1, so the candidates are the three in S3. Flutter and Ollama are not installed; no `.env`, so no LLM is configured locally.
- L5 Decisions: chunks are windows of 3 pages with a 1-page overlap inside each part, plus one chunk per summary tool: 58 chunks of 91-364 words. NFKC normalization fixes ligatures ("signiﬁca"). Lexical search is OR over Spanish stems. The Postgres host port is 5433 because PORTFOLIO-AUDIT uses 5432. The `KnowledgeRetriever` test passed on its first run (no RED observed); it was written alongside a trivial implementation.
- L6 Next: T4 grounded replies in the companion and API, then T5 evaluation to pick the default model and mode.
- L7 Engram mirror pending: the session is bound to project `linkedin-post-skill` and refuses writes to `puente-salud-mental` (`session_project_mismatch`). The local document is the source of truth until it syncs.
- L8 T4 decisions: references are appended to the unchanged system prompt as `[n]` entries; citations are numbered per reply instead of using raw chunk ids, which small models mangle less. The ungrounded response shape is unchanged (empty `sources` is omitted). New `GET /ready`; `/health` is unchanged.
