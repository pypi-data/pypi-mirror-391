from dateutil.relativedelta import relativedelta
from edc_consent.consent_definition import ConsentDefinition
from edc_lab_panel.panels import fbc_panel, lft_panel, rft_panel, vl_panel
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import (
    Crf,
    CrfCollection,
    Requisition,
    RequisitionCollection,
    Visit,
)
from edc_visit_schedule.visit_schedule import VisitSchedule


def get_visit_schedule(
    cdef: ConsentDefinition,
    crfs: CrfCollection | None = None,
    requisitions: RequisitionCollection | None = None,
    visit_schedule_name: str | None = None,
    schedule_name: str | None = None,
    onschedule_model: str | None = None,
    offschedule_model: str | None = None,
    visit_count: int | None = None,
    allow_unscheduled: bool | None = None,
):
    visit_schedule_name = visit_schedule_name or "visit_schedule"
    schedule_name = schedule_name or "schedule"
    onschedule_model = onschedule_model or "edc_visit_schedule.onschedule"
    offschedule_model = offschedule_model or "clinicedc_tests.offschedule"
    visit_count = visit_count or 2
    allow_unscheduled = True if allow_unscheduled is None else allow_unscheduled

    crfs = crfs or CrfCollection(
        Crf(show_order=1, model="clinicedc_tests.crflongitudinalone", required=True),
        Crf(show_order=2, model="clinicedc_tests.crflongitudinaltwo", required=True),
        Crf(show_order=3, model="clinicedc_tests.crfthree", required=True),
        Crf(show_order=4, model="clinicedc_tests.crffour", required=True),
        Crf(show_order=5, model="clinicedc_tests.crffive", required=True),
        Crf(show_order=6, model="clinicedc_tests.crfsix", required=True),
        Crf(show_order=7, model="clinicedc_tests.crfseven", required=True),
        Crf(show_order=8, model="clinicedc_tests.bloodresultsfbc", required=True),
        Crf(show_order=9, model="clinicedc_tests.crfencrypted", required=True),
    )

    requisitions = requisitions or RequisitionCollection(
        Requisition(show_order=30, panel=fbc_panel, required=True, additional=False),
        Requisition(show_order=40, panel=lft_panel, required=True, additional=False),
        Requisition(show_order=50, panel=rft_panel, required=True, additional=False),
        Requisition(show_order=60, panel=vl_panel, required=True, additional=False),
    )

    crfs_unscheduled = CrfCollection(
        Crf(show_order=801, model="clinicedc_tests.crfeight", required=True),
        Crf(show_order=201, model="clinicedc_tests.crftwo", required=True),
        Crf(show_order=101, model="clinicedc_tests.crfone", required=True),
    )

    crfs_missed = CrfCollection(
        Crf(show_order=1000, model="edc_visit_tracking.subjectvisitmissed", required=True),
    )

    visits = []
    for index in range(0, visit_count):
        visits.append(  # noqa: PERF401
            Visit(
                code=f"{index + 1}000",
                title=f"Day {index + 1}",
                timepoint=index,
                rbase=relativedelta(months=index),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
                requisitions=requisitions,
                crfs=crfs,
                crfs_unscheduled=crfs_unscheduled,
                crfs_missed=crfs_missed,
                allow_unscheduled=allow_unscheduled,
            )
        )

    schedule = Schedule(
        name=schedule_name,
        onschedule_model=onschedule_model,
        offschedule_model=offschedule_model,
        consent_definitions=[cdef],
        appointment_model="edc_appointment.appointment",
    )

    for visit in visits:
        schedule.add_visit(visit)

    visit_schedule = VisitSchedule(
        name=visit_schedule_name,
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="edc_adverse_event.deathreport",
    )

    visit_schedule.add_schedule(schedule)
    return visit_schedule
