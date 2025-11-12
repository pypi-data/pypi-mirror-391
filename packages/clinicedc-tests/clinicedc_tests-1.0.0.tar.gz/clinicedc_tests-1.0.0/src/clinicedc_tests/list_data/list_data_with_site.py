from clinicedc_constants import OTHER
from edc_list_data.row import Row

list_data = {
    "clinicedc_tests.antibiotic": [
        Row(("amoxicillin_ampicillin", "Amoxicillin/Ampicillin"), extra="uganda"),
        ("ceftriaxone", "Ceftriaxone"),
        ("ciprofloxacin", "Ciprofloxacin"),
        ("doxycycline", "Doxycycline"),
        ("erythromycin", "Erythromycin"),
        ("flucloxacillin", "Flucloxacillin"),
        ("gentamicin", "Gentamicin"),
        (OTHER, "Other, specify"),
    ],
}
