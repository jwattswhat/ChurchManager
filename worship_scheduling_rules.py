"""UI-free rules for worship participant availability and staffing plans."""

from dataclasses import dataclass


def serialized_values(value):
    text = str(value or "").replace("[", "").replace("]", "")
    for separator in (";", "\r", "\n"):
        text = text.replace(separator, ",")
    return [item.strip().strip("'\"") for item in text.split(",") if item.strip().strip("'\"")]


def time_text(value):
    if value is None:
        return None
    if hasattr(value, "hour"):
        return f"{value.hour:02d}:{value.minute:02d}"
    if hasattr(value, "total_seconds"):
        seconds = int(value.total_seconds()) % 86400
        return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}"
    pieces = str(value).split(":")
    return ":".join(piece.zfill(2) for piece in pieces[:2]) if len(pieces) >= 2 else str(value)


def pattern_matches(pattern, starts_at, season):
    _pattern_id, _description, service_time, days, months, seasons = pattern[:6]
    if service_time is not None and starts_at.strftime("%H:%M") != time_text(service_time):
        return False
    filters = (
        (serialized_values(days), starts_at.strftime("%A")),
        (serialized_values(months), starts_at.strftime("%B")),
        (serialized_values(seasons), str(season or "")),
    )
    return all(not values or "All" in values or current in values for values, current in filters)


@dataclass(frozen=True)
class AssignmentSuggestion:
    role_id: int
    role: str
    participant_id: int
    participant: str


def _position_slots(requirements, assignments, requirement_values, assignment_values):
    unused = list(assignments)
    slots = []
    for requirement in requirements:
        role_id, role, required_count = requirement_values(requirement)
        matching = [
            assignment for assignment in unused
            if assignment_values(assignment)[0] == role_id
            and assignment_values(assignment)[3] != "DECLINED"
        ]
        for slot in range(1, int(required_count) + 1):
            assignment = matching.pop(0) if matching else None
            if assignment:
                unused.remove(assignment)
            slots.append((role_id, role, slot, int(required_count), assignment, True))
    for assignment in unused:
        role_id, role, _name, _status = assignment_values(assignment)
        slots.append((role_id, role, None, None, assignment, False))
    return slots


def required_position_rows(requirements, assignments):
    """Build screen rows from repository tuple records."""
    return _position_slots(
        requirements,
        assignments,
        lambda row: (row[1], row[2], row[3]),
        lambda row: (row[1], row[2], row[4], row[5]),
    )


def report_participant_rows(requirements, assignments):
    """Build report rows using the same slot-filling rules as the service screen."""
    slots = _position_slots(
        requirements,
        assignments,
        lambda row: (row["WorshipRoleID"], row["Role"], row["RequiredCount"]),
        lambda row: (row["WorshipRoleID"], row["Role"], row["Name"], row["Status"]),
    )
    rows = []
    for _role_id, role, slot, total, assignment, required in slots:
        position = f"{role} {slot}" if required and total > 1 else role
        if assignment:
            rows.append({
                "Role": position,
                "Name": assignment["Name"],
                "Status": str(assignment["Status"]).title(),
            })
        else:
            rows.append({"Role": position, "Name": "Unfilled", "Status": "Open"})
    return rows


class SchedulingSuggestionService:
    def __init__(self, repository):
        self.repository = repository

    def suggest(self, service_id):
        context = self.repository.service_context(service_id)
        if not context:
            raise ValueError("The selected Worship Service is unavailable.")
        requirements = self.repository.requirements(service_id)
        if not requirements:
            raise ValueError("No participant-role requirements are configured for this Order of Service.")
        existing = self.repository.assignments(service_id)
        counts = {}
        used_for_role = {}
        for row in existing:
            if row[5] != "DECLINED":
                counts[row[1]] = counts.get(row[1], 0) + 1
            used_for_role.setdefault(row[1], set()).add(row[3])
        suggestions = []
        for _requirement_id, role_id, role, required in requirements:
            missing = max(0, int(required) - counts.get(role_id, 0))
            candidates = self.repository.eligible_candidates(role_id, context[2], context[4])
            available = [row for row in candidates if row[0] not in used_for_role.get(role_id, set())]
            suggestions.extend(
                AssignmentSuggestion(role_id, role, participant[0], participant[1])
                for participant in available[:missing]
            )
        return suggestions

    def apply(self, service_id, suggestions):
        return self.repository.save_suggestions(service_id, suggestions)
