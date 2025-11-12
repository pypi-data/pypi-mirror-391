from __future__ import annotations

from typing import TYPE_CHECKING

from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.models import Appointment
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.utils import get_related_visit_model_cls

if TYPE_CHECKING:
    from edc_visit_tracking.models import SubjectVisit

__all__ = ["create_related_visit"]


def create_related_visit(
    appointment: Appointment, reason: str | None = None
) -> SubjectVisit:
    if not appointment.related_visit:
        related_visit = get_related_visit_model_cls().objects.create(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=appointment.appt_datetime,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            visit_code_sequence=appointment.visit_code_sequence,
            reason=reason or SCHEDULED,
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save_base(update_fields=["appt_status"])
        appointment.refresh_from_db()
    else:
        related_visit = appointment.related_visit
    return related_visit
