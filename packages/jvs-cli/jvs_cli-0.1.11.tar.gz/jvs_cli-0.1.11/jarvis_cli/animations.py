def typewriter_effect_chunks(text: str, chunk_size: int = 3) -> list[str]:
    if not text:
        return []
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[:i + chunk_size])
    if chunks and chunks[-1] != text:
        chunks.append(text)
    return chunks
