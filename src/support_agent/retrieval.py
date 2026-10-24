def split_into_chunks(text):
    chunks = []
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            chunks.append(cleaned)

    return chunks