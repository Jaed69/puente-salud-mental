"""Retrieval evaluation: labelled questions, ranking metrics and a Markdown report.

Each question is labelled with the printed book pages that answer it. A chunk is relevant when it
covers at least one of those pages, so labels survive re-chunking.

- Hit@k: share of questions with at least one relevant chunk in the top k.
- Recall@k: share of a question's relevant chunks found in the top k, averaged over questions.
- MRR: mean reciprocal rank of the first relevant chunk (0 when none is returned).
"""

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

DEFAULT_KS = (1, 3, 5, 10)


@dataclass(frozen=True)
class EvalQuestion:
    question_id: str
    question: str
    pages: frozenset[int]


@dataclass(frozen=True)
class QuestionScores:
    hit: dict[int, float]
    recall: dict[int, float]
    reciprocal_rank: float


@dataclass(frozen=True)
class Summary:
    hit: dict[int, float]
    recall: dict[int, float]
    mrr: float
    questions: int


def load_questions(path: Path) -> list[EvalQuestion]:
    questions: list[EvalQuestion] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["id"] in seen:
            raise ValueError(f"duplicate question id: {row['id']}")
        if not row["pages"]:
            raise ValueError(f"question {row['id']} has no labelled pages")
        seen.add(row["id"])
        questions.append(EvalQuestion(row["id"], row["question"], frozenset(row["pages"])))
    return questions


def relevant_chunk_ids(
    question: EvalQuestion, chunk_pages: Mapping[str, Iterable[int]]
) -> set[str]:
    return {
        chunk_id for chunk_id, pages in chunk_pages.items() if question.pages.intersection(pages)
    }


def score_ranking(
    ranked_ids: Sequence[str], relevant: set[str], ks: Sequence[int] = DEFAULT_KS
) -> QuestionScores:
    if not relevant:
        raise ValueError("a question needs at least one relevant chunk")
    hit = {}
    recall = {}
    for k in ks:
        found = relevant.intersection(ranked_ids[:k])
        hit[k] = 1.0 if found else 0.0
        recall[k] = len(found) / len(relevant)
    first = next((rank for rank, cid in enumerate(ranked_ids, 1) if cid in relevant), None)
    return QuestionScores(hit, recall, 1.0 / first if first else 0.0)


def summarize(scores: Sequence[QuestionScores]) -> Summary:
    count = len(scores)
    ks = scores[0].hit.keys()
    return Summary(
        hit={k: sum(s.hit[k] for s in scores) / count for k in ks},
        recall={k: sum(s.recall[k] for s in scores) / count for k in ks},
        mrr=sum(s.reciprocal_rank for s in scores) / count,
        questions=count,
    )


def render_report(
    results: Mapping[tuple[str, str], Summary],
    *,
    latency_ms: Mapping[tuple[str, str], float],
    ks: Sequence[int] = DEFAULT_KS,
    context: str,
) -> str:
    """Markdown table, best configuration first (by MRR, then Hit@k from the largest k)."""
    ordered = sorted(
        results.items(),
        key=lambda item: (item[1].mrr, *(item[1].hit[k] for k in reversed(ks))),
        reverse=True,
    )
    header = (
        "| model | mode | "
        + " | ".join(f"Hit@{k}" for k in ks)
        + " | "
        + " | ".join(f"Recall@{k}" for k in ks)
        + " | MRR | p50 latency (ms) |"
    )
    divider = "|" + "---|" * (2 + 2 * len(ks) + 2)
    rows = []
    for (model, mode), summary in ordered:
        cells = [model, mode]
        cells += [f"{summary.hit[k]:.2f}" for k in ks]
        cells += [f"{summary.recall[k]:.2f}" for k in ks]
        cells += [f"{summary.mrr:.3f}", f"{latency_ms[(model, mode)]:.0f}"]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(
        [
            "# Retrieval evaluation",
            "",
            context,
            "",
            "Hit@k: share of questions with a relevant chunk in the top k. Recall@k: share of "
            "each question's relevant chunks in the top k. MRR: mean reciprocal rank of the "
            "first relevant chunk. A chunk is relevant when it covers a labelled page.",
            "",
            header,
            divider,
            *rows,
            "",
        ]
    )
