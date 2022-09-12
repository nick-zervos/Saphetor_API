
import json
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
import os
from .read_file import read_vcf
from pathlib import Path
# Create your tests here.



#Tests for the endpoints are done using the "APIClient" virtual client to make calls to our API

#Tests that the file exists and is not empty
class TestVcfFile(TestCase):
    def setUp(self):
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')
        
        #test that the file can be found at the root folder of the application
    def test_file_exists(self):
        file_path = self.filepath
        vcf_file = read_vcf(file_path)
        self.assertIsNotNone(vcf_file)

        #test that there was no error and that the DataFrame created from the file is not empty
    def test_file_not_empty(self):
        file_path = self.filepath
        vcf_file = read_vcf(file_path)
        self.assertFalse(vcf_file.empty)



#test get method functionality
class TestGetMethod(TestCase):
    def setUp(self):
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')

    #make a get request. Expect response status 200
    def test_get_method(self):
        client = APIClient()
        request = client.get(reverse('get-data'))
        self.assertEqual(request.status_code, 200)

    #test that we get a 200 status code when the accept header is set to json
    def test_get_with_json_format(self):
        client = APIClient()
        request = client.get(reverse('get-data'), HTTP_ACCEPT='application/json')
        self.assertEqual(request.status_code, 200)

    #test that we get a 200 status code when the accept header is set to xml
    def test_get_with_xml_format(self):
        client = APIClient()
        request = client.get(reverse('get-data'), HTTP_ACCEPT='application/xml')
        self.assertEqual(request.status_code, 200)
        
    #test that we get a 406 status code when accept header is set to something other than json or xml, for example, javascript
    def test_get_other_types(self): 
        client = APIClient()
        request = client.get(reverse('get-data'), HTTP_ACCEPT='application/javascript')
        self.assertEqual(request.status_code, 406)

    #retrieve the first 1d from the DataFrame, and test the get method with that ID. Expect a 200 status code
    def test_get_by_id(self): 
        test_file = read_vcf(self.filepath)
        first_row = test_file.iloc[0]
        test_id = first_row['ID']
        client = APIClient()
        request = client.get(reverse('get-data'), {'id' : test_id}, HTTP_ACCEPT='application/json')
        self.assertEqual(request.status_code, 200)

    #test that we get a 404 error when sending an id that does not exist in the file
    def test_get_by_non_existant_id(self):
        client = APIClient()
        request = client.get(reverse('get-data'), {'id' : 123456}, HTTP_ACCEPT='application/json')
        self.assertEqual(request.status_code, 404)

    #test for pagination. The "next" field may have value of null but will always be present if pagination is set correctly
    def test_for_pagination(self): 
        client = APIClient()
        request = client.get(reverse('get-data'), HTTP_ACCEPT='application/json')
        self.assertIn('next', request.data)


# test post method functionality
class TestPostMethodCases(TestCase):
    def setUp(self):
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')

    #test that a post request can be made using our predefined authorization header . Expect a 201 status code
    def test_predefined_secret_valid(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        request = client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json',)
        self.assertEqual(request.status_code, 201)

    #test that the post request fails when given an invalid authorization header. Expect a 403 status code
    def test_post_with_invalid_token(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='invalid')
        request = client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json')
        self.assertEqual(request.status_code, 403)

    #test that our application correctly validates the data type send by the client and returns a 415 status code when given data in a form other than json
    def test_post_invalid_content_type(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        request = client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/xml')
        self.assertEqual(request.status_code, 415)


    #test that our application validates that data sent by the client (optional task from Post request)
    def test_post_invalid_data(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        request = client.post(reverse('post-data'), data=json.dumps({"CHROM": "chA", "POS": "1000", "ALT": "34", "REF": "ABC", "ID": "rst4524"}), content_type='application/json')
        self.assertEqual(request.status_code, 403)

    #test that the post request actually adds the data to the file
    def test_post_succeded(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret',)
        client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json',)
        vcf_file = read_vcf(self.filepath)
        found_rows = vcf_file.loc[vcf_file["ID"] == 'rs123']
        row_added = False if found_rows.empty else True    
        client.delete(reverse('delete-data')+'?id=rs123', content_type='application/json')
        self.assertTrue(row_added)


#test put method functionality
class TestPutMethodCases(TestCase):
    def setUp(self):
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')

    #test that the application successfully changes the data in the file based on the data sent by the client
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


    def test_put_method_with_no_id(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        request = client.put(reverse('put-data'), data=json.dumps({"CHROM": "chr22", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json')
        self.assertEqual(request.status_code, 403)


    def test_put_method_with_no_records_found(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        request = client.put(reverse('put-data')+'?id=123456789', data=json.dumps({"CHROM": "chr22", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json')
        self.assertEqual(request.status_code, 404)


#test delete method functionality
class TestDeleteMethodCases(TestCase):
    def setUp(self):
        self.filepath = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')

    #test that the application deletes the rows from the file
    def test_delete_method(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token secret')
        client.post(reverse('post-data'), data=json.dumps({"CHROM": "chr1", "POS": 1000, "ALT": "A", "REF": "G", "ID": "rs123"}), content_type='application/json')
        request = client.delete(reverse('delete-data')+'?id=rs123', content_type='application/json')
        vcf_file = read_vcf(self.filepath)
        row_deleted = vcf_file.loc[vcf_file["ID"] == 'rs123']
        was_row_deleted = True if row_deleted.empty else False
        self.assertTrue(was_row_deleted)



    