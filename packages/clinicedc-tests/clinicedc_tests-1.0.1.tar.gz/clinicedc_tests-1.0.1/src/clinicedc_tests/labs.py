from django.conf import settings
from edc_lab import LabProfile, Process, bc, pl, site_labs
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

lab_profile = LabProfile(
    name="lab_profile",
    requisition_model=settings.SUBJECT_REQUISITION_MODEL,
    reference_range_collection_name="my_reportables",
)

# every panel refered to in the visit schedule must be here as well
lab_profile.add_panel(fbc_panel)
lab_profile.add_panel(lft_panel)
lab_profile.add_panel(rft_panel)
lab_profile.add_panel(hba1c_panel)
lab_profile.add_panel(cd4_panel)
lab_profile.add_panel(lipids_panel)
lab_profile.add_panel(insulin_panel)
lab_profile.add_panel(sputum_panel)
lab_profile.add_panel(blood_glucose_panel)

vl_pl_process = Process(aliquot_type=pl, aliquot_count=4)
vl_bc_process = Process(aliquot_type=bc, aliquot_count=2)
vl_panel.processing_profile.add_processes(vl_pl_process, vl_bc_process)
lab_profile.add_panel(vl_panel)

site_labs.register(lab_profile)
