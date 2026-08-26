"""Pure validation helpers for selected worship hymns."""


def normalize_tune(value):
    """Normalize a tune name for exact, case-insensitive comparison."""
    return " ".join(str(value or "").split()).casefold()


def duplicate_selection_status(lines):
    """Return line statuses plus duplicate-hymn and duplicate-tune counts."""
    hymn_counts = {}
    tune_hymns = {}
    for line in lines:
        hymn_id = line.get("hymn_id")
        if hymn_id is None:
            continue
        hymn_counts[hymn_id] = hymn_counts.get(hymn_id, 0) + 1
        tune = normalize_tune(line.get("tune"))
        if tune:
            tune_hymns.setdefault(tune, set()).add(hymn_id)
    duplicate_tunes = {tune for tune, hymn_ids in tune_hymns.items() if len(hymn_ids) > 1}
    statuses = []
    for line in lines:
        hymn_id = line.get("hymn_id")
        tune = normalize_tune(line.get("tune"))
        if hymn_id is not None and hymn_counts.get(hymn_id, 0) > 1:
            statuses.append("DUPLICATE HYMN")
        elif tune in duplicate_tunes:
            statuses.append("DUPLICATE TUNE")
        else:
            statuses.append("")
    hymn_duplicates = sum(count - 1 for count in hymn_counts.values() if count > 1)
    tune_duplicates = sum(len(tune_hymns[tune]) - 1 for tune in duplicate_tunes)
    return statuses, hymn_duplicates, tune_duplicates
