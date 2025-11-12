from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

clinicedc_tests_admin = EdcAdminSite(
    name="clinicedc_tests_admin", app_label=AppConfig.name
)
