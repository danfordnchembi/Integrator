from django.test import TestCase, RequestFactory

from Core import views as core_views
import os
import json

class ValidatorsTestCase(TestCase):
    def test_svcrec_transformation(self):
        with open('resources/svcrec.json') as f:
            data = json.load(f)
            result = core_views.refine_service_received_payload(data)

    def test_ddc_transformation(self):
        with open('resources/ddc.json') as f:
            data = json.load(f)
            result = core_views.refine_death_within_facility_payload(data)