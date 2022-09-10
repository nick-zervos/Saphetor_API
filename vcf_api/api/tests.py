import json
from django.test import TestCase
from rest_framework.test import APIRequestFactory, RequestsClient, APIClient
from django.urls import reverse
import os
from . import read_file
from pathlib import Path
import pandas as pd
# Create your tests here.



class TestGetMethodCases(TestCase):
    def setUp(self) -> None:
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')

    def test_the_get(self):
        client = APIClient()
        request = client.get(reverse('get-data'))
        self.assertEqual(request.status_code, 200)

    def test_get_json(self):
        client = APIClient()
        request = client.get(reverse('get-data'), HTTP_ACCEPT='application/json')
        self.assertEqual(request.status_code, 200)

    def test_get_xml(self):
        client = APIClient()
        request = client.get(reverse('get-data'), HTTP_ACCEPT='application/xml')
        self.assertEqual(request.status_code, 200)
        
    def test_get_other_types(self):
        client = APIClient()
        request = client.get(reverse('get-data'), HTTP_ACCEPT='application/javascript')
        self.assertEqual(request.status_code, 406)

    def test_get_by_id(self):
        test_file = read_file.read_vcf(self.filepath)
        first_row = test_file.iloc[0]
        test_id = first_row['ID']
        client = APIClient()
        request = client.get(reverse('get-data'), {'id' : test_id}, HTTP_ACCEPT='application/json')
        self.assertEqual(request.status_code, 200)

    def test_get_by_non_existant_id(self):
        client = APIClient()
        request = client.get(reverse('get-data'), {'id' : 123456}, HTTP_ACCEPT='application/json')
        self.assertEqual(request.status_code, 404)

    def test_for_pagination(self):
        client = APIClient()
        request = client.get(reverse('get-data'), HTTP_ACCEPT='application/json')
        self.assertIn('next', request.data)