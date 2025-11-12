from dateutil.relativedelta import relativedelta
from edc_consent.consent_definition import ConsentDefinition
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, CrfCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule


def get_visit_schedule(cdef: ConsentDefinition):
    crfs = CrfCollection(
        Crf(show_order=1, model="clinicedc_tests.crffour", required=True),
    )

    visit_schedule = VisitSchedule(
        name="visit_schedule",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="edc_adverse_event.deathreport",
        locator_model="edc_locator.subjectlocator",
    )

    schedule = Schedule(
        name="schedule",
        onschedule_model="edc_visit_schedule.onschedule",
        offschedule_model="edc_visit_schedule.offschedule",
        consent_definitions=[cdef],
        appointment_model="edc_appointment.appointment",
    )

    visits = []
    for index in range(0, 4):
        visits.append(  # noqa: PERF401
            Visit(
                code=f"{index + 1}000",
                title=f"Day {index + 1}",
                timepoint=index,
                rbase=relativedelta(months=index),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
                requisitions=None,
                crfs=crfs,
                allow_unscheduled=False,
            )
        )
    for visit in visits:
        schedule.add_visit(visit)

    visit_schedule.add_schedule(schedule)
    return visit_schedule
