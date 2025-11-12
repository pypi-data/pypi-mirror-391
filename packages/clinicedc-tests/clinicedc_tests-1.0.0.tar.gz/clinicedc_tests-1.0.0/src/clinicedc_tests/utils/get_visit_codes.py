from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_visit_tracking.models import SubjectVisit


def get_visit_codes(
    model_cls: type[Appointment | SubjectVisit], order_by: str | None = None
):
    return [
        f"{o.visit_code}.{o.visit_code_sequence}"
        for o in model_cls.objects.all().order_by(order_by)
    ]
