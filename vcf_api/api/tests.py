
import json
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
import os
from .read_file import read_vcf
from pathlib import Path
# Create your tests here.





#Tests that the file exists and is not empty
class TestVcfFile(TestCase):
    def setUp(self):
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')
        
    def test_file_exists(self):
        file_path = self.filepath
        vcf_file = read_vcf(file_path)
        self.assertIsNotNone(vcf_file)

    def test_file_not_empty(self):
        file_path = self.filepath
        vcf_file = read_vcf(file_path)
        self.assertFalse(vcf_file.empty)



#test get method functionality
class TestGetMethod(TestCase):
    def setUp(self):
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')

    def test_get_method(self):
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
        
    def test_get_other_types(self): #expect 406 not allowed
        client = APIClient()
        request = client.get(reverse('get-data'), HTTP_ACCEPT='application/javascript')
        self.assertEqual(request.status_code, 406)

    def test_get_by_id(self): #retrieve an id from the file for valid test
        test_file = read_vcf(self.filepath)
        first_row = test_file.iloc[0]
        test_id = first_row['ID']
        client = APIClient()
        request = client.get(reverse('get-data'), {'id' : test_id}, HTTP_ACCEPT='application/json')
        self.assertEqual(request.status_code, 200)

    def test_get_by_non_existant_id(self):
        client = APIClient()
        request = client.get(reverse('get-data'), {'id' : 123456}, HTTP_ACCEPT='application/json')
        self.assertEqual(request.status_code, 404)

    def test_for_pagination(self): #next may have value of null but will always be present
        client = APIClient()
        request = client.get(reverse('get-data'), HTTP_ACCEPT='application/json')
        self.assertIn('next', request.data)


# test post method functionality
class TestPostMethodCases(TestCase):
    def setUp(self):
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')

    def test_predefined_secret_valid(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        request = client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json',)
        self.assertEqual(request.status_code, 201)

    def test_post_with_invalid_token(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='invalid')
        request = client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json')
        self.assertEqual(request.status_code, 403)

    def test_post_invalid_content_type(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        request = client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/xml')
        self.assertEqual(request.status_code, 415)

    def test_post_invalid_data(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        request = client.post(reverse('post-data'), data=json.dumps({"CHROM": "chA", "POS": "1000", "ALT": "34", "REF": "ABC", "ID": "rst4524"}), content_type='application/json')
        self.assertEqual(request.status_code, 403)


    def test_post_succeded(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret',)
        client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json',)
        vcf_file = read_vcf(self.filepath)
        found_rows = vcf_file.loc[vcf_file["ID"] == 'rs123']
        row_added = False if found_rows.empty else True    
        client.delete(reverse('delete-data')+'?id=rs123', content_type='application/json')
        self.assertTrue(row_added)
        

class TestPutMethodCases(TestCase):
    def setUp(self):
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')

    def test_put_method(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json',)
        client.put(reverse('put-data')+'?id=rs123', data=json.dumps({"CHROM": "chr22", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json')
        vcf_file = read_vcf(self.filepath)
        row_edited = vcf_file.loc[vcf_file["ID"] == 'rs123']
        was_row_changed = True if row_edited['CHROM'].values[0] == 'chr22' else False
        client.delete(reverse('delete-data')+'?id=rs123', content_type='application/json')
        self.assertTrue(was_row_changed)


class TestDeleteMethodCases(TestCase):
    def setUp(self):
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')


    def test_delete_method(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json')
        request = client.delete(reverse('delete-data')+'?id=rs123', content_type='application/json')
        vcf_file = read_vcf(self.filepath)
        row_deleted = vcf_file.loc[vcf_file["ID"] == 'rs123']
        was_row_deleted = True if row_deleted.empty else False
        self.assertTrue(was_row_deleted)



    