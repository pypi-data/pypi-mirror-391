from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from edc_appointment.constants import IN_PROGRESS_APPT
from edc_appointment.creators import create_unscheduled_appointment
from edc_appointment.utils import get_appointment_model_cls
from edc_visit_tracking.constants import UNSCHEDULED

if TYPE_CHECKING:
    from edc_appointment.models import Appointment

__all__ = ["get_appointment"]


def get_appointment(
    subject_identifier: str | None = None,
    visit_code: str | None = None,
    visit_code_sequence: int | None = None,
    reason: str | None = None,
    appt_datetime: datetime | None = None,
    timepoint: float | Decimal | None = None,
) -> Appointment:
    if timepoint is not None:
        appointment = get_appointment_model_cls().objects.get(
            subject_identifier=subject_identifier,
            timepoint=timepoint,
            visit_code_sequence=visit_code_sequence,
        )
    else:
        appointment = get_appointment_model_cls().objects.get(
            subject_identifier=subject_identifier,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
        )
    if appt_datetime:
        appointment.appt_datetime = appt_datetime
        appointment.save()
        appointment.refresh_from_db()
    if reason == UNSCHEDULED:
        appointment = create_unscheduled_appointment(appointment)
    appointment.appt_status = IN_PROGRESS_APPT
    appointment.save()
    appointment.refresh_from_db()
    return appointment
