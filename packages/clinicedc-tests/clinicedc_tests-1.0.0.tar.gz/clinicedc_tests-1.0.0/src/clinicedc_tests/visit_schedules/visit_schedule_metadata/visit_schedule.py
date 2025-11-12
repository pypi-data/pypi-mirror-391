from dateutil.relativedelta import relativedelta
from edc_lab_panel.panels import (
    blood_glucose_panel,
    cd4_panel,
    fbc_panel,
    hba1c_panel,
    insulin_panel,
    lft_panel,
    lipids_panel,
    rft_panel,
    sputum_panel,
    vl_panel,
)
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import (
    Crf,
    CrfCollection,
    Requisition,
    RequisitionCollection,
    Visit,
)
from edc_visit_schedule.visit_schedule import VisitSchedule

from ..dummy_panel import DummyPanel

app_label = "clinicedc_tests"


def get_visit_schedule(cdef):
    class MockPanel(DummyPanel):
        """`requisition_model` is normally set when the lab profile
        is set up.
        """

        def __init__(self, name):
            super().__init__(requisition_model="clinicedc_tests.subjectrequisition", name=name)

    crfs_prn = CrfCollection(
        Crf(show_order=100, model=f"{app_label}.prnone"),
        Crf(show_order=200, model=f"{app_label}.prntwo"),
    )

    crfs_missed = CrfCollection(
        Crf(
            show_order=1000,
            model="edc_visit_tracking.subjectvisitmissed",
            required=True,
        ),
    )

    crfs0 = CrfCollection(
        Crf(show_order=1, model=f"{app_label}.crfthree", required=True),
        Crf(show_order=2, model=f"{app_label}.crffour", required=True),
        Crf(show_order=3, model=f"{app_label}.crffive", required=True),
        Crf(show_order=4, model=f"{app_label}.crfsix", required=True),
        Crf(show_order=5, model=f"{app_label}.crfseven", required=True),
    )

    crfs1 = CrfCollection(
        Crf(show_order=1, model=f"{app_label}.crfsix", required=True),
        Crf(show_order=2, model=f"{app_label}.crfseven", required=True),
        Crf(show_order=3, model=f"{app_label}.crfeight", required=True),
    )

    crfs2 = CrfCollection(Crf(show_order=1, model=f"{app_label}.crfseven", required=True))

    crfs_unscheduled = CrfCollection(
        Crf(show_order=1, model=f"{app_label}.crffour", required=True),
        Crf(show_order=2, model=f"{app_label}.crffive", required=True),
        Crf(show_order=3, model=f"{app_label}.crfseven", required=True),
    )

    requisitions = RequisitionCollection(
        Requisition(show_order=10, panel=fbc_panel, required=True, additional=False),
        Requisition(show_order=20, panel=lft_panel, required=True, additional=False),
        Requisition(show_order=30, panel=vl_panel, required=False, additional=False),
        Requisition(show_order=40, panel=rft_panel, required=False, additional=False),
        Requisition(show_order=50, panel=hba1c_panel, required=False, additional=False),
        Requisition(show_order=60, panel=cd4_panel, required=False, additional=False),
        Requisition(show_order=70, panel=lipids_panel, required=False, additional=False),
        Requisition(show_order=80, panel=insulin_panel, required=False, additional=False),
    )

    requisitions3000 = RequisitionCollection(
        Requisition(show_order=10, panel=lipids_panel, required=True, additional=False)
    )

    requisitions_unscheduled = RequisitionCollection(
        Requisition(show_order=10, panel=sputum_panel, required=True, additional=False),
        Requisition(show_order=20, panel=blood_glucose_panel, required=True, additional=False),
        Requisition(show_order=30, panel=MockPanel("five"), required=True, additional=False),
        Requisition(show_order=90, panel=MockPanel("nine"), required=True, additional=False),
    )

    visit0 = Visit(
        code="1000",
        title="Week 1",
        timepoint=0,
        rbase=relativedelta(days=0),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        requisitions=requisitions,
        crfs=crfs0,
        crfs_unscheduled=crfs_unscheduled,
        crfs_prn=crfs_prn,
        requisitions_unscheduled=requisitions_unscheduled,
        allow_unscheduled=True,
        facility_name="5-day-clinic",
    )

    visit1 = Visit(
        code="2000",
        title="Week 2",
        timepoint=1,
        rbase=relativedelta(days=7),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        requisitions=requisitions,
        crfs=crfs1,
        crfs_prn=crfs_prn,
        crfs_missed=crfs_missed,
        facility_name="5-day-clinic",
    )

    visit2 = Visit(
        code="3000",
        title="Week 3",
        timepoint=2,
        rbase=relativedelta(days=14),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        requisitions=requisitions3000,
        crfs=crfs2,
        crfs_prn=crfs_prn,
        facility_name="5-day-clinic",
    )

    schedule = Schedule(
        name="schedule",
        onschedule_model="edc_visit_schedule.onschedule",
        offschedule_model="clinicedc_tests.offschedule",
        consent_definitions=[cdef],
        appointment_model="edc_appointment.appointment",
    )

    schedule.add_visit(visit0)
    schedule.add_visit(visit1)
    schedule.add_visit(visit2)

    visit_schedule = VisitSchedule(
        name="visit_schedule",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="clinicedc_tests.deathreport",
    )

    visit_schedule.add_schedule(schedule)
    return visit_schedule
