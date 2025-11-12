from dateutil.relativedelta import relativedelta
from edc_consent.consent_definition import ConsentDefinition
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, CrfCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

crfs_prn = CrfCollection(
    Crf(show_order=100, model="clinicedc_tests.prnone"),
)
crfs = CrfCollection(
    Crf(show_order=10, model="clinicedc_tests.team", required=True),
    Crf(show_order=20, model="clinicedc_tests.venue", required=True),
    Crf(show_order=30, model="clinicedc_tests.teamwithdifferentfields", required=True),
)


def get_visit_schedule(consent_definition: ConsentDefinition):
    visit = Visit(
        code="1000",
        timepoint=0,
        rbase=relativedelta(days=0),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        requisitions=None,
        crfs=crfs,
        crfs_prn=crfs_prn,
        requisitions_unscheduled=None,
        crfs_unscheduled=None,
        allow_unscheduled=False,
        facility_name="5-day-clinic",
    )

    schedule = Schedule(
        name="schedule",
        onschedule_model="edc_visit_schedule.onschedule",
        offschedule_model="clinicedc_tests.offschedule",
        appointment_model="edc_appointment.appointment",
        consent_definitions=[consent_definition],
    )

    visit_schedule = VisitSchedule(
        name="visit_schedule",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="edc_adverse_event.deathreport",
    )

    schedule.add_visit(visit)

    visit_schedule.add_schedule(schedule)
    return visit_schedule
