from dateutil.relativedelta import relativedelta
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


class Panel(DummyPanel):
    """`requisition_model` is normally set when the lab profile
    is set up.
    """

    def __init__(self, name):
        super().__init__(requisition_model="clinicedc_tests.subjectrequisition", name=name)


crfs = CrfCollection(
    Crf(show_order=1, model="clinicedc_tests.crfone", required=True),
    Crf(show_order=2, model="clinicedc_tests.crftwo", required=True),
    Crf(show_order=3, model="clinicedc_tests.crfthree", required=True),
    Crf(show_order=4, model="clinicedc_tests.crffour", required=True),
    Crf(show_order=5, model="clinicedc_tests.crffive", required=True),
)

requisitions = RequisitionCollection(
    Requisition(show_order=10, panel=Panel("one"), required=True, additional=False),
    Requisition(show_order=20, panel=Panel("two"), required=True, additional=False),
    Requisition(show_order=30, panel=Panel("three"), required=True, additional=False),
    Requisition(show_order=40, panel=Panel("four"), required=True, additional=False),
    Requisition(show_order=50, panel=Panel("five"), required=True, additional=False),
    Requisition(show_order=60, panel=Panel("six"), required=True, additional=False),
)


def get_visit_schedule(cdef, allow_unscheduled: bool | None = None):
    allow_unscheduled = True if allow_unscheduled is None else allow_unscheduled
    visit_schedule = VisitSchedule(
        name="visit_schedule1",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="clinicedc_tests.deathreport",
        locator_model="edc_locator.subjectlocator",
    )

    schedule = Schedule(
        name="schedule1",
        onschedule_model="clinicedc_tests.onscheduleone",
        offschedule_model="clinicedc_tests.offscheduleone",
        consent_definitions=[cdef],
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
                requisitions=requisitions,
                crfs=crfs,
                allow_unscheduled=allow_unscheduled,
            )
        )
    for visit in visits:
        schedule.add_visit(visit)

    visit_schedule.add_schedule(schedule)

    return visit_schedule
