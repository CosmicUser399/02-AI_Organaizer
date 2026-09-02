"""Embeddings and semantic search over note paragraphs."""

import logging
import math

from sqlalchemy.orm import Session

from app import models
from app.services.openai_client import openai_client

logger = logging.getLogger(__name__)

MAX_CHUNK_CHARS = 4000
MIN_CHUNK_CHARS = 8
DEFAULT_TOP_K = 5
MIN_SIMILARITY = 0.2


def split_into_paragraphs(content: str) -> list[str]:
    """Split note content into searchable paragraph chunks.

    Args:
        content: Full note text

    Returns:
        Non-empty paragraph strings ready for embedding
    """
    if not content or not content.strip():
        return []

    raw_blocks = content.replace("\r\n", "\n").split("\n\n")
    chunks: list[str] = []
    for block in raw_blocks:
        stripped = block.strip()
        if not stripped:
            continue
        if len(stripped) <= MAX_CHUNK_CHARS:
            if len(stripped) >= MIN_CHUNK_CHARS:
                chunks.append(stripped)
            continue
        for line in stripped.split("\n"):
            piece = line.strip()
            if len(piece) < MIN_CHUNK_CHARS:
                continue
            if len(piece) > MAX_CHUNK_CHARS:
                piece = piece[:MAX_CHUNK_CHARS]
            chunks.append(piece)
    return chunks


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Return cosine similarity of two embedding vectors.

    Args:
        left: First vector
        right: Second vector

    Returns:
        Similarity in range [-1, 1], or 0.0 if invalid
    """
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    norm_left = math.sqrt(sum(a * a for a in left))
    norm_right = math.sqrt(sum(b * b for b in right))
    if norm_left == 0.0 or norm_right == 0.0:
        return 0.0
    return dot / (norm_left * norm_right)


def index_note(db: Session, note: models.Note) -> int:
    """Rebuild embedding chunks for a note.

    Existing chunks are replaced. Does not commit the session.

    Args:
        db: Database session
        note: Note whose content should be indexed

    Returns:
        Number of chunks stored
    """
    db.query(models.NoteChunk).filter(
        models.NoteChunk.note_id == note.id
    ).delete()

    paragraphs = split_into_paragraphs(note.content)
    if not paragraphs:
        db.flush()
        logger.info("Note id=%d has no indexable paragraphs", note.id)
        return 0

    embeddings = openai_client.get_embeddings(paragraphs)
    if len(embeddings) != len(paragraphs):
        raise ValueError("Embedding count does not match paragraphs")
    for text, embedding in zip(paragraphs, embeddings):
        db.add(
            models.NoteChunk(
                note_id=note.id,
                text=text,
                embedding=embedding,
            )
        )
    db.flush()
    logger.info(
        "Indexed note id=%d with %d chunks",
        note.id,
        len(paragraphs),
    )
    return len(paragraphs)


def ensure_notes_indexed(db: Session) -> None:
    """Index notes that do not yet have embedding chunks."""
    notes = db.query(models.Note).all()
    for note in notes:
        if note.chunks:
            continue
        try:
            index_note(db, note)
        except Exception as exc:
            logger.warning(
                "Failed to index note id=%d: %s",
                note.id,
                str(exc),
            )


def _generate_answer(question: str, matches: list[dict]) -> str:
    """Write a short answer from retrieved note fragments.

    Args:
        question: User question
        matches: Ranked chunk dicts with note_title and chunk_text

    Returns:
        Answer text in the language of the question
    """
    if not matches:
        return "Не удалось найти релевантные фрагменты в заметках."

    snippets = []
    for item in matches:
        snippets.append(f"- [{item['note_title']}]: {item['chunk_text']}")
    context = "\n".join(snippets)
    system_message = (
        "You answer the user using only the provided note "
        "fragments. Reply in the same language as the question. "
        "Be concise (2-4 sentences). If the fragments are not "
        "enough, say so and quote the closest snippet."
    )
    prompt = f"Question: {question}\n\n" f"Note fragments:\n{context}"
    return openai_client.chat_completion(
        prompt=prompt,
        system_message=system_message,
        temperature=0.3,
    )


def search_notes(
    db: Session,
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> tuple[list[dict], str]:
    """Find note paragraphs semantically similar to a question.

    Args:
        db: Database session
        question: Natural-language question
        top_k: Maximum number of fragments to return

    Returns:
        Tuple of (match dicts, generated answer)
    """
    cleaned = question.strip()
    if not cleaned:
        return [], "Задайте вопрос по своим заметкам."

    ensure_notes_indexed(db)
    db.flush()

    chunks = (
        db.query(models.NoteChunk)
        .filter(models.NoteChunk.embedding.isnot(None))
        .all()
    )
    if not chunks:
        logger.info("No note chunks available for search")
        return [], (
            "Пока нет проиндексированных заметок. "
            "Создайте или сохраните заметку и повторите поиск."
        )

    query_embedding = openai_client.get_embedding(cleaned)
    scored: list[tuple[float, models.NoteChunk]] = []
    for chunk in chunks:
        if not chunk.embedding:
            continue
        score = cosine_similarity(query_embedding, chunk.embedding)
        if score >= MIN_SIMILARITY:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    limit = max(1, top_k)
    top = scored[:limit]

    matches: list[dict] = []
    for score, chunk in top:
        note = chunk.note
        matches.append(
            {
                "note_id": note.id if note else chunk.note_id,
                "note_title": note.title if note else "",
                "chunk_text": chunk.text,
                "score": round(float(score), 4),
            }
        )

    try:
        answer = _generate_answer(cleaned, matches)
    except Exception as exc:
        logger.warning("Failed to generate search answer: %s", str(exc))
        answer = ""

    logger.info(
        "Semantic search returned %d matches for question",
        len(matches),
    )
    return matches, answer
