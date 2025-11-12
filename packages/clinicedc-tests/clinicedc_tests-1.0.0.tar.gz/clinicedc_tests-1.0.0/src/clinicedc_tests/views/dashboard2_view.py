from edc_dashboard.view_mixins import EdcViewMixin
from edc_dashboard.views import DashboardView as BaseDashboardView


class Dashboard2View(EdcViewMixin, BaseDashboardView):
    dashboard_url_name = "test_dashboard2_url"
    dashboard_template_name = "subject_dashboard_template"
