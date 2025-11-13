from edc_lab.identifiers import RequisitionIdentifier
from faker.providers import BaseProvider


class EdcLabProvider(BaseProvider):
    def requisition_identifier(self):
        return RequisitionIdentifier().identifier
