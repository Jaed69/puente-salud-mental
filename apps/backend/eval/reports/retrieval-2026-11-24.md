# Retrieval evaluation

Run 2026-11-24 on 58 chunks and 60 questions (`eval/retrieval_questions.jsonl`). Questions are colloquial Peruvian Spanish written and labelled by the assistant, not reviewed by clinicians. Latency includes the local query embedding on CPU.

Hit@k: share of questions with a relevant chunk in the top k. Recall@k: share of each question's relevant chunks in the top k. MRR: mean reciprocal rank of the first relevant chunk. A chunk is relevant when it covers a labelled page.

| model | mode | Hit@1 | Hit@3 | Hit@5 | Hit@10 | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR | p50 latency (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| jinaai/jina-embeddings-v2-base-es | hybrid | 0.47 | 0.70 | 0.82 | 0.92 | 0.21 | 0.41 | 0.52 | 0.70 | 0.618 | 18 |
| intfloat/multilingual-e5-large | hybrid | 0.47 | 0.65 | 0.78 | 0.87 | 0.22 | 0.39 | 0.53 | 0.65 | 0.587 | 44 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | hybrid | 0.42 | 0.73 | 0.77 | 0.87 | 0.19 | 0.42 | 0.51 | 0.64 | 0.573 | 7 |
| jinaai/jina-embeddings-v2-base-es | dense | 0.43 | 0.63 | 0.78 | 0.88 | 0.18 | 0.37 | 0.50 | 0.65 | 0.565 | 16 |
| intfloat/multilingual-e5-large | dense | 0.40 | 0.60 | 0.70 | 0.78 | 0.18 | 0.39 | 0.48 | 0.59 | 0.517 | 43 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | dense | 0.32 | 0.55 | 0.70 | 0.80 | 0.12 | 0.27 | 0.38 | 0.53 | 0.469 | 5 |
| (none) | lexical | 0.33 | 0.52 | 0.60 | 0.77 | 0.16 | 0.33 | 0.39 | 0.56 | 0.460 | 1 |

## Reading

- Hybrid search beats dense-only search for every model: +0.05 MRR (jina), +0.07 (e5) and +0.10
  (MiniLM). It also beats lexical-only search (MRR 0.460). Fusing Spanish full-text with vectors
  pays off on colloquial questions whose words do not appear in the book.
- Default chosen: `jinaai/jina-embeddings-v2-base-es` in hybrid mode. It has the best MRR (0.618),
  Hit@5 (0.82) and Hit@10 (0.92), a p50 of 18 ms with the query embedded on CPU, and a 0.64 GB
  model, against 2.24 GB for e5-large.
- With 60 questions, gaps of about 0.03 MRR (jina vs e5 in hybrid mode) are within noise. The
  ranking dense < hybrid is consistent across all three models.
- Recall@k stays well below Hit@k because a labelled concept often spans several overlapping
  chunks. The companion receives the top 4 (`PUENTE_RETRIEVAL_K`); Hit@3 to Hit@5 is the relevant
  range.

## Limitations

- The assistant wrote and labelled the questions. Peruvian psychologists did not review them, and
  they are not real user messages. The research notes ask for 100-300 clinician-labelled pairs
  before trusting these numbers for model choice in production.
- One source (58 chunks). Scores will move when the corpus grows.
- Retrieval only. Answer faithfulness (do replies stay true to the cited chunks?) is not measured
  yet.

## Next improvements to measure against this baseline

1. A cross-encoder reranker over the top 20-50.
2. Contextual chunk headers generated per chunk (Anthropic's contextual retrieval).
3. A larger, clinician-reviewed question set, plus a faithfulness check of grounded replies.
