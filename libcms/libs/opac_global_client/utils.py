def join_url(*parts: str):
    cleaned_parts = []
    for i, part in enumerate(parts):
        if i == 0 and len(parts) > 1:
            cleaned_parts.append(part.rstrip('/'))
        else:
            cleaned_parts.append(part.lstrip('/'))

    return '/'.join(cleaned_parts)
