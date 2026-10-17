# Agent orchestration frameworks and guardrail tooling for a safety-critical, stateful, multi-agent mental-health chatbot (Python/FastAPI) — 2026

Scope note: research budget was ~15 tool calls. Several official doc fetches (AWS Bedrock languages page, Meta Llama Guard 4 card) failed with ECONNRESET/redirect, so some facts rely on search snippets of the official pages. Items not verified this session are explicitly marked "UNVERIFIED (prior knowledge)" and live in Inferences/Gaps, not in Cited Findings.

## 1. Orchestration framework comparison (LangGraph, OpenAI Agents SDK, Claude Agent SDK, PydanticAI, Google ADK, CrewAI, LlamaIndex Workflows, no-framework)

### Takeaway
LangGraph 1.0 (GA 22 Oct 2025, no-breaking-changes-until-2.0 commitment) is the best-verified fit for an explicit, auditable, persisted state machine with human-in-the-loop interrupts; the OpenAI Agents SDK has the most developed built-in guardrail/tripwire primitives but its guardrails only run on the first agent's input and the last agent's output, which is a structural gap for a three-role design. A thin plain-Python state machine remains a credible option if determinism/auditability outweighs framework features.

### Cited Findings
- LangChain and LangGraph both reached v1.0 on October 22, 2025, in Python and TypeScript; LangGraph is positioned as the lower-level runtime for customized, long-running agents; the team committed to no breaking changes until 2.0; `langgraph.prebuilt` is deprecated with functionality moved to `langchain.agents` — [LangChain blog](https://blog.langchain.com/langchain-langgraph-1dot0); [LangChain forum announcement](https://forum.langchain.com/t/we-launched-1-0-versions-of-langchain-and-langgraph/1904)
- The 1.0 alpha was announced 2 Sep 2025 with a late-October target, which was met — [LangChain blog (alpha)](https://www.langchain.com/blog/langchain-langchain-1-0-alpha-releases)
- LangGraph `interrupt()` requires a checkpointer; resuming uses `Command(resume=...)` keyed by a thread ID; in-memory saver is for tests, SQLite for local dev, Postgres for production — [rentierdigital blog (secondary)](https://rentierdigital.xyz/blog/human-in-the-loop-langgraph); [DEV Community (secondary)](https://dev.to/jamesbmour/interrupts-and-commands-in-langgraph-building-human-in-the-loop-workflows-4ngl)
- A reported LangGraph 1.0.1 issue on self-hosted Docker: the stream emits an interrupt but the thread state's interrupts list is empty (no resolution found) — [LangChain forum](https://forum.langchain.com/t/interrupt-inconsistency-langgraph-1-x/1996)
- `langgraph-checkpoint` is a separately versioned package (1.0.x line on PyPI) — [PyPI](https://pypi.org/project/langgraph-checkpoint/1.0.7)
- LangGraph Platform was renamed "LangSmith Deployment" (Oct 2025); LangGraph is the open-source framework, LangSmith Deployment is the managed service; deployment tiers historically included a free limited self-hosted tier (up to 1M nodes executed) and Self-Hosted Enterprise — [LangChain LangGraph Platform page](https://www.langchain.com/langgraph-platform); [LangChain announcement](https://www.langchain.com/blog/langgraph-platform-announce)
- LangSmith and LangGraph Platform are available in AWS Marketplace (July 2025) — [LangChain blog](https://blog.langchain.com/aws-marketplace-july-2025-announce)
- OpenAI Agents SDK guardrails: "Input guardrails run only for the first agent in the chain"; "Output guardrails run only for the agent that produces the final output"; tool guardrails wrap function tools before/after execution, but "tool guardrails do not apply to the handoff call itself" — [OpenAI Agents SDK docs: Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- OpenAI Agents SDK input guardrails default to `run_in_parallel=True` (concurrent with the agent; "the agent may have already consumed tokens and executed tools before being cancelled"); blocking mode (`run_in_parallel=False`) means "the agent never executes" if the tripwire fires; output guardrails always run after completion — [OpenAI Agents SDK docs: Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- Tripwire triggers raise an exception that halts execution; exceptions carry the triggering result — [OpenAI Agents SDK docs: Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- Handoffs in the OpenAI Agents SDK are modeled as tool calls (e.g., `transfer_to_<agent_name>`) — [traeai learning notes (secondary)](https://learn.traeai.com/t/ai-engineering/phases/14-agent-engineering/16-openai-agents-sdk.html)
- The OpenAI Agents SDK PyPI page states support for OpenAI Responses and Chat Completions APIs "as well as 100+ other LLMs" — [PyPI openai-agents](https://pypi.org/p/openai-agents)

### Inferences
- For this design (guardian must check BOTH user input before the companion/RAG agents run AND every agent output before it reaches the user), the OpenAI Agents SDK's "first-agent input / last-agent output" guardrail scope is insufficient on its own after handoffs; the guardian should be modeled as explicit graph nodes rather than relying on framework guardrail hooks. In the Agents SDK, input guardrails must be set to blocking (`run_in_parallel=False`) for fail-closed behavior.
- LangGraph's explicit nodes/edges + checkpointer per thread map naturally to: `guardian_input -> route(companion|rag|crisis) -> guardian_output -> deliver|escalate(interrupt)`; checkpoints give an audit trail of state transitions. Interrupts give a native "pause for human clinician" mechanism. The reported interrupt/stream inconsistency means escalation should not rely solely on streamed interrupt events; persist an escalation record in your own DB.
- LangGraph OSS can be self-hosted inside FastAPI with a Postgres checkpointer without using LangSmith Deployment, which limits lock-in to the open-source library (license of OSS repo: UNVERIFIED this session — prior knowledge says MIT).
- UNVERIFIED (prior knowledge): PydanticAI offers typed/validated structured outputs (useful for guardian verdict schemas) and multi-provider support incl. Bedrock and Anthropic; Google ADK supports non-Gemini models via LiteLLM; CrewAI is role/crew-oriented and less suited to deterministic control flow; LlamaIndex Workflows is event-driven and strong for RAG; Claude Agent SDK is oriented toward autonomous tool-using agents (Claude Code harness) and is Anthropic-centric (Bedrock/Vertex supported as Claude backends), not a general multi-provider state-graph orchestrator. These need verification against official docs before inclusion in a final report.
- Plain-Python state machine: maximal determinism, testability (pure functions per state), and zero lock-in; cost is re-implementing persistence, streaming, and HITL resume. Reasonable if the graph is small (3 roles, fixed routes).

### Gaps
- Could not verify in this session: current versions/stability of PydanticAI, Google ADK, CrewAI, LlamaIndex Workflows, Claude Agent SDK; their Bedrock support; their HITL/persistence primitives.
- No official source fetched confirming the OpenAI Agents SDK works with Amazon Bedrock (via LiteLLM extension) — search returned nothing specific.
- OSS license of LangGraph not confirmed by a source this session.
- No source fetched on LangGraph streaming modes (`stream_mode` values) to mobile clients over SSE/WebSocket.

## 2. Guardrail tooling, and which detect self-harm in Spanish reliably

### Takeaway
No tool has published, Spanish-specific self-harm recall numbers that I could find; Spanish is officially covered by Amazon Bedrock Guardrails (since Dec 2024), Llama Guard 3 (8 languages incl. Spanish; Llama Guard 4 card says "optimized for English"), NeMo Guardrails' Nemotron content-safety multilingual rail (9 languages incl. `es`), and OpenAI omni-moderation (claimed better non-English performance, no language list). ShieldGemma is primarily English. Every option requires local evaluation on Peruvian Spanish self-harm data.

### Cited Findings
- Amazon Bedrock Guardrails added Spanish and French support in December 2024 — [AWS What's New](https://aws.amazon.com/about-aws/whats-new/2024/12/amazon-bedrock-guardrails-languages-spanish-french)
- Bedrock Guardrails language support has two levels: "Optimized and supported" (models tuned and tested for the language) vs "Supported" (tested but not tuned); coverage for text content filters depends on tier — [AWS docs: Languages supported by Bedrock Guardrails](https://docs.aws.eu/bedrock/latest/userguide/guardrails-supported-languages.html)
- Bedrock Classic tier supports English, French, Spanish; Standard tier has more comprehensive language support and requires cross-Region inference — [AWS docs: Safeguard tiers](https://docs.aws.eu/bedrock/latest/userguide/guardrails-tiers.html)
- AWS warns guardrails are ineffective with unsupported languages and recommends testing the intended languages — [AWS docs: supported languages](https://docs.aws.eu/bedrock/latest/userguide/guardrails-supported-languages.html)
- Llama Guard 4 uses the MLCommons hazard taxonomy S1–S14, with S11 = "Suicide & Self-Harm" — [NVIDIA NIM docs](https://docs.api.nvidia.com/nim/reference/meta-llama-guard-4-12b)
- S11 covers responses that enable, encourage, or endorse suicide, self-injury, or disordered eating — [DeepInfra model card copy](https://deepinfra.com/meta-llama/Llama-Guard-4-12B)
- Meta's Llama Guard 4 card states the model was optimized for English and developers should test other languages — [Meta model card (search snippet)](https://developer.meta.com/ai/docs/model-cards-and-prompt-formats/llama-guard-4/)
- Llama Guard (3) supports 8 languages: English, French, German, Hindi, Italian, Portuguese, Spanish, Thai — [PolyGuard paper (arXiv 2504.04377)](https://arxiv.org/pdf/2504.04377) (via search snippet)
- ShieldGemma models primarily classify English-language text into six safety categories — [PolyGuard paper](https://arxiv.org/pdf/2504.04377) (via search snippet)
- Llama Guard, ShieldGemma and Granite Guardian offer some non-English support but performance is often suboptimal vs English — [arXiv 2508.01710](https://arxiv.org/pdf/2508.01710v3) (via search snippet)
- The same paper claims Llama-3.1-Nemotron-Safety-Guard-Multilingual-8B-v1 is the only multilingual safety guard with a commercially-friendly license (authors' claim) — [arXiv 2508.01710](https://arxiv.org/pdf/2508.01710v3)
- PolyGuard: 17-language moderation model/dataset, PolyGuardPrompts 29K samples, reported +5.5% over existing open-weight and commercial classifiers; reliance on GPT-4o-generated labels may affect commercial viability — [arXiv 2504.04377](https://arxiv.org/pdf/2504.04377); [Moonlight review](https://themoonlight.io/review/polyguard-a-multilingual-safety-moderation-tool-for-17-languages)
- NeMo Guardrails content-safety rail with `nvidia/llama-3.1-nemotron-safety-guard-8b-v3` supports multilingual detection/refusal in 9 languages including Spanish (`es`), with English fallback; enabled via `rails.config.content_safety.multilingual`; requires `pip install nemoguardrails[multilingual]` (fast-langdetect); per-language refusal messages configurable — [NeMo Guardrails docs: Content Safety](https://docs.nvidia.com/nemo/guardrails/latest/configure-rails/guardrail-catalog/content-safety.html); [Release notes 0.20.0](https://docs.nvidia.com/nemo/guardrails/0.20.0/about/release-notes.html); [Multilingual tutorial](https://docs.nvidia.com/nemo/microservices/latest/guardrails/tutorials/multilingual-safety.html)
- OpenAI omni-moderation-latest (GPT-4o based, Sept 2024) is "more accurate than our previous model, especially in non-English languages"; self-harm family includes self-harm, self-harm/intent, self-harm/instructions, and these accept images — [OpenAI announcement](https://openai.com/index/upgrading-the-moderation-API-with-our-new-multimodal-moderation-model/)
- A 42% improvement on a multilingual test set is reported by a secondary guide citing OpenAI internal evals (not confirmed in OpenAI docs) — [eesel.ai (secondary)](https://www.eesel.ai/blog/openai-moderation-api)

### Inferences
- For a Bedrock-centric stack, Bedrock Guardrails is the lowest-friction first-line content filter in Spanish, but its content filter categories (hate, insults, sexual, violence, misconduct, prompt attack — UNVERIFIED prior knowledge) do not include a dedicated self-harm category; self-harm likely needs a denied-topic policy or a separate classifier. Verify.
- Llama Guard 3 (explicit Spanish) may be a safer open-weight choice than Llama Guard 4 for Spanish self-harm until Spanish eval data exists. Nemotron Safety Guard multilingual is the strongest documented multilingual open option with NeMo integration.
- OpenAI moderation exposes the most clinically useful granularity (intent vs instructions) but adds a non-AWS data processor — a data-residency/privacy consideration for health data in Peru.
- "Reliably detects self-harm in Spanish": no source supports that claim for any tool; treat all as needing a local, clinician-labeled Spanish (Peruvian colloquial) eval set measuring recall at fixed false-positive rates.

### Gaps
- Exact Bedrock per-policy language table (content filters Standard tier, denied topics, contextual grounding check, automated reasoning) — official page fetch failed; contextual grounding Spanish support unverified.
- Guardrails AI validators, Azure AI Content Safety (self-harm severity levels, language list), IBM Granite Guardian 3.x language coverage, ShieldGemma 2 — not researched this session.
- No head-to-head Spanish self-harm benchmark found for any of these tools.
- Whether NeMo `self check input/output` (LLM-prompt-based) behaves well in Spanish depends on the underlying LLM; no NVIDIA doc found.

## 3. Best-practice architecture for the guardian (layering, pre/post checks, latency, fail-closed, LLM-as-judge weaknesses, audit logging)

### Takeaway
Published practice converges on defense-in-depth: an independent safety layer outside the conversational LLM, per-turn risk scoring with conversation history, multiple heterogeneous detectors, and explicit escalation policies; blocking (not parallel) input checks are needed for fail-closed behavior.

### Cited Findings
- Defense-in-depth case study (Ash): a purpose-built model plus an independent embeddings-based safeguard trained on real usage data; end-to-end false negative rate of 0.38% among sessions flagged by their LLM judge, presented as a lower bound — [arXiv 2601.17003](https://www.arxiv.org/pdf/2601.17003)
- Multi-turn safety architecture: a safety classifier scores risk at every turn using full conversation history, tested with GPT-5-chat and Qwen3.5-27B — [arXiv 2607.22692](https://arxiv.org/pdf/2607.22692)
- Prompt-based sensitivity tuning: across five sensitivity levels on one LLM with 200 clinician-labeled segments from a deployed chatbot, missed-risk rate fell from 87% to 0% as sensitivity rose (with more false positives); most sensitive variants reached near-perfect recall with sub-second latency — [Weber et al., medRxiv Jan 2026](https://www.medrxiv.org/content/10.64898/2026.01.12.26343914.full.pdf); [Centre for Suicide Prevention summary](https://www.suicideinfo.ca/resource/suicide-and-crisis-risk-detection-using-large-language-models-in-mental-health-chatbots/)
- Parallel guardrails can let the agent consume tokens and run tools before cancellation; blocking mode prevents execution entirely — [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/guardrails/)

### Inferences
- Recommended layering: (1) deterministic Spanish keyword/regex + lexicon for crisis phrases (incl. Peruvian colloquialisms) → immediate crisis route, ~ms latency, high recall; (2) a fast classifier (Bedrock Guardrails / Llama Guard 3 / Nemotron Safety Guard) on input and output; (3) LLM-as-judge with a written rubric (constitution) for nuanced risk and grounding, run blocking before delivery. Use an OR-combination for risk (any layer flags → escalate), favoring recall per Weber et al.
- Fail-closed: on guardian timeout/error, return a safe templated response with crisis resources (e.g., Peru's Línea 113 opción 5 — UNVERIFIED, confirm) rather than the model output.
- Streaming tension: output checks require buffering; options are buffer-then-stream, or stream with sentence-level chunk checks and a kill switch. Input checks must complete before generation starts.
- UNVERIFIED (prior knowledge): LLM-as-judge known weaknesses include position/verbosity bias, self-preference bias when judge and generator share a model family (use a different model family for the judge), and susceptibility to prompt injection embedded in the judged content; rubric/"constitutional" judging with structured JSON verdicts improves consistency. Sources (e.g., Zheng et al. 2023 "Judging LLM-as-a-Judge", arXiv 2306.05685; Panickssery et al. 2024 on self-preference) should be verified.
- Audit logging: persist per turn the input, each detector's verdict + version, judge rationale, route taken, final output, and escalation events, keyed by thread ID; LangGraph checkpoints can serve as part of this but a separate append-only audit table is safer.

### Gaps
- No primary source fetched on concrete latency budgets for guard models (e.g., Bedrock Guardrails p50/p95).
- LLM-as-judge bias literature not fetched this session.

## 4. Patterns published specifically for mental-health chatbots

### Takeaway
2026 literature describes safety layers that sit outside the LLM, detect risk across turns, map signals to clinical escalation policies, and choose an escalation path while keeping the conversation supportive — i.e., "classify crisis, then route" architectures validated against clinician ratings.

### Cited Findings
- Safety governance architecture external to the LLM: detects risk across turns, checks signals against clinical escalation policies, chooses an escalation path while maintaining supportive conversation; evaluated against licensed psychologists' ratings (results not visible on pages seen) — [Research Square rs-10279940](https://www.researchsquare.com/article/rs-10279940/v1)
- Detection framed as a real-time monitoring problem rather than offline accuracy — [Weber et al., medRxiv](https://www.medrxiv.org/content/10.64898/2026.01.12.26343914.full.pdf)
- Multi-turn per-turn risk scoring architecture ("Risk Governance for Generative AI Mental Health Support") — [arXiv 2607.22692](https://arxiv.org/pdf/2607.22692)
- Two-layer defense-in-depth in a deployed mental-health product (Ash) — [arXiv 2601.17003](https://www.arxiv.org/pdf/2601.17003)
- An EA Forum post evaluates LLMs for suicide-risk detection (non-peer-reviewed) — [EA Forum](https://forum.effectivealtruism.org/posts/CKykK8LWdqGsJuTK8/evaluating-llms-for-suicide-risk-detection-can-ai-catch-a-1)

### Inferences
- The three-role design (companion, RAG, guardian with human escalation) matches the published "external safety layer + escalation policy" pattern; the guardian should evaluate the whole conversation history each turn, not just the last message, since risk is often cumulative.
- Sensitivity should be tuned for recall with human review absorbing false positives, consistent with Weber et al.

### Gaps
- Full results of the Research Square study and arXiv 2607.22692 were not read (only snippets).
- No Spanish-language or Latin American mental-health chatbot safety study found this session.
- Regulatory guidance (e.g., Peru MINSA, FDA/WHO guidance on digital mental health) not researched.
