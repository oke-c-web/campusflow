"""Report building (Engineer B)."""

from validation import CATEGORIES, PRIORITIES, STATUSES


def build_report(tickets):
    by_status = {s: 0 for s in STATUSES}
    by_priority = {p: 0 for p in PRIORITIES}
    by_category = {c: 0 for c in CATEGORIES}
    for t in tickets:  # each ticket counted exactly once per breakdown
        by_status[t["status"]] += 1
        by_priority[t["priority"]] += 1
        by_category[t["category"]] += 1

    total = len(tickets)
    resolved = by_status["resolved"]
    unresolved = by_status["open"] + by_status["in_progress"]
    percentage = round(resolved / total * 100, 1) if total else 0.0
    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
        "unresolved": unresolved,
        "resolved": resolved,
        "resolution_percentage": percentage,
    }


def format_report(report):
    lines = [f"Total tickets: {report['total']}",
             f"Unresolved: {report['unresolved']}",
             f"Resolved: {report['resolved']}",
             f"Resolution: {report['resolution_percentage']:g}%"]
    for title, key in (("status", "by_status"), ("priority", "by_priority"),
                       ("category", "by_category")):
        lines += ["", f"By {title}:"]
        lines += [f"  {k:<12} {v}" for k, v in report[key].items()]
    return "\n".join(lines)
