import json

import pytest

from puente.knowledge.evaluation import (
    EvalQuestion,
    load_questions,
    relevant_chunk_ids,
    render_report,
    score_ranking,
    summarize,
)

CHUNK_PAGES = {
    "a": (10, 11, 12),
    "b": (12, 13, 14),
    "c": (20, 21),
    "d": (30,),
}


def test_relevant_chunks_are_those_overlapping_the_labelled_pages():
    question = EvalQuestion("q1", "¿pregunta?", frozenset({12}))

    assert relevant_chunk_ids(question, CHUNK_PAGES) == {"a", "b"}


def test_score_ranking_reports_hits_recall_and_reciprocal_rank():
    relevant = {"a", "b"}

    scores = score_ranking(["c", "b", "d", "a"], relevant, ks=(1, 3, 5))

    assert scores.hit == {1: 0.0, 3: 1.0, 5: 1.0}
    assert scores.recall == {1: 0.0, 3: 0.5, 5: 1.0}
    assert scores.reciprocal_rank == pytest.approx(0.5)


def test_score_ranking_without_relevant_results_is_zero():
    scores = score_ranking(["c", "d"], {"a"}, ks=(1, 3))

    assert scores.hit == {1: 0.0, 3: 0.0}
    assert scores.recall == {1: 0.0, 3: 0.0}
    assert scores.reciprocal_rank == 0.0


def test_summarize_averages_per_question_scores():
    first = score_ranking(["a"], {"a"}, ks=(1,))
    second = score_ranking(["c", "a"], {"a"}, ks=(1,))

    summary = summarize([first, second])

    assert summary.hit == {1: 0.5}
    assert summary.mrr == pytest.approx(0.75)
    assert summary.questions == 2


def test_load_questions_reads_jsonl_and_rejects_duplicates(tmp_path):
    path = tmp_path / "questions.jsonl"
    rows = [
        {"id": "q1", "question": "uno", "pages": [12, 13]},
        {"id": "q2", "question": "dos", "pages": [30]},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    questions = load_questions(path)

    assert questions[0] == EvalQuestion("q1", "uno", frozenset({12, 13}))
    path.write_text("\n".join(json.dumps(row) for row in [rows[0], rows[0]]), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate question id"):
        load_questions(path)


def test_render_report_has_one_row_per_configuration_best_first():
    good = summarize([score_ranking(["a"], {"a"}, ks=(1, 5))])
    bad = summarize([score_ranking(["c"], {"a"}, ks=(1, 5))])

    report = render_report(
        {("model-x", "lexical"): bad, ("model-y", "hybrid"): good},
        latency_ms={("model-x", "lexical"): 3.0, ("model-y", "hybrid"): 40.0},
        ks=(1, 5),
        context="58 chunks, 1 question",
    )

    lines = [line for line in report.splitlines() if line.startswith("| model-")]
    assert lines[0].startswith("| model-y | hybrid | 1.00 | 1.00 |")
    assert lines[1].startswith("| model-x | lexical | 0.00 | 0.00 |")
    assert "58 chunks, 1 question" in report
