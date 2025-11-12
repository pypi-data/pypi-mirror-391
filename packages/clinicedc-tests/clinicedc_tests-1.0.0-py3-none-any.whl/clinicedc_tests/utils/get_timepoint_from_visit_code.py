from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal


def get_timepoint_from_visit_code(
    instance,
    visit_code: str,
) -> float | Decimal | None:
    timepoint = None
    for v in instance.schedule.visits.timepoints:
        if v.name == visit_code:
            timepoint = v.timepoint
            break
    return timepoint
