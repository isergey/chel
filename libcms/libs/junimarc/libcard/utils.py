from typing import List

from junimarc.marc_query import SubfieldQuery


def repeat(sfq: SubfieldQuery, delimiter: str) -> str:
    sfq_list = sfq.list()
    sfq_list_len = len(sfq_list)
    if sfq_list_len == 0:
        return ''
    if sfq_list_len == 1:
        return sfq_list[0].d().strip()

    parts = []
    for i, sf in enumerate(sfq_list):
        data = sf.d().strip()
        if data:
            if i > 0:
                parts.append(delimiter)
            parts.append(data)
    return ''.join(parts)


def join(parts: List[str], delimiter: str):
    parts_len = len(parts)
    if parts_len == 0:
        return ''

    if parts_len == 1:
        return parts[0].strip()

    not_empty_parts = []
    delimiter_fs = delimiter[0] if delimiter else ''
    for part in parts:
        part = part.strip()
        if not part:
            continue

        part_ls = part[-1]
        if delimiter_fs and part_ls == delimiter_fs:
            part = part[0:-1]

        if not part:
            continue
        part = part.strip()
        not_empty_parts.append(part)

    return delimiter.join(not_empty_parts)


def wrap(prefix: str, text: str, suffix: str) -> str:
    if not text:
        return ''

    return ''.join([prefix, text, suffix])


def suffix(text: str, suf: str) -> str:
    text = text.strip()
    if not text:
        return ''
    if text.endswith(suf):
        return text

    return text + suf
