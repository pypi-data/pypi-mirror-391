from django.urls import include, path, re_path
from django.views.generic import RedirectView
from edc_listboard.views import SubjectListboardView
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_subject_dashboard.views import SubjectDashboardView

from .admin_site import clinicedc_tests_admin
from .views import Dashboard2View, DashboardView

app_name = "clinicedc_tests"

urlpatterns = [
    path("clinicedc_tests/admin/", clinicedc_tests_admin.urls),
    path("clinicedc_tests/", clinicedc_tests_admin.urls),
    *SubjectListboardView.urls(
        url_names_key="subject_listboard_url",
        namespace=app_name,
        identifier_pattern=ResearchProtocolConfig().subject_identifier_pattern,
    ),
    *SubjectDashboardView.urls(
        url_names_key="subject_dashboard_url",
        namespace=app_name,
        identifier_pattern=ResearchProtocolConfig().subject_identifier_pattern,
    ),
    *DashboardView.urls(
        namespace=app_name,
        url_names_key="test_dashboard_url",
    ),
    *Dashboard2View.urls(
        namespace=app_name,
        url_names_key="test_dashboard2_url",
    ),
    path("i18n/", include("django.conf.urls.i18n")),
    re_path(".", RedirectView.as_view(url="/"), name="home_url"),
    path("", RedirectView.as_view(url="admin/"), name="logout"),
]
