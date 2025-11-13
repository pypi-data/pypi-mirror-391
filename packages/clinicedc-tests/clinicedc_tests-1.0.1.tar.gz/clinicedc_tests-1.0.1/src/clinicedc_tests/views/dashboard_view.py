from edc_dashboard.view_mixins import EdcViewMixin
from edc_dashboard.views import DashboardView as BaseDashboardView


class DashboardView(EdcViewMixin, BaseDashboardView):
    dashboard_url_name = "test_dashboard_url"
    dashboard_template = "clinicedc_tests/test_dashboard.html"
