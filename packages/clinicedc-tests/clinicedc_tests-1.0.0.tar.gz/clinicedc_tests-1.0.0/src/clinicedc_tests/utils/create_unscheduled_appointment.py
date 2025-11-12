# from __future__ import annotations
#
# from typing import TYPE_CHECKING
#
# from edc_appointment.constants import INCOMPLETE_APPT
# from edc_appointment.creators import UnscheduledAppointmentCreator
#
# if TYPE_CHECKING:
#     from edc_appointment.models import Appointment
#
# __all__ = ["create_unscheduled_appointment"]
#
#
# def create_unscheduled_appointment(appointment: Appointment) -> Appointment:
#     appointment.appt_status = INCOMPLETE_APPT
#     appointment.save()
#     appointment.refresh_from_db()
#     appt_creator = UnscheduledAppointmentCreator(
#         subject_identifier=appointment.subject_identifier,
#         visit_schedule_name=appointment.visit_schedule_name,
#         schedule_name=appointment.schedule_name,
#         visit_code=appointment.visit_code,
#         suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
#         facility=appointment.facility,
#     )
#     return appt_creator.appointment
