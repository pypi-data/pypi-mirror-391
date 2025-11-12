from clinicedc_constants import NO
from edc_form_label import CustomLabelCondition


class MyCustomLabelCondition(CustomLabelCondition):
    def check(self, **kwargs):  # noqa: ARG002
        if self.previous_obj:
            return self.previous_obj.circumcised == NO
        return False
