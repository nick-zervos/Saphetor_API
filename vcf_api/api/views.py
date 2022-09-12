import json
import os
from .read_file import read_vcf, get_vcf_header, read_original_vcf
from pathlib import Path
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes, parser_classes
from rest_framework.renderers import JSONRenderer
from rest_framework import pagination
#required for returning xml
from rest_framework_xml.renderers import XMLRenderer
import pandas as pd
from .validation import validate_post_request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .authentication import PredefinedSecret
from rest_framework.parsers import JSONParser
import csv




@api_view(['GET'])
#decorator that returns json or xml depending on the HTTP_ACCEPT header the client sent
@renderer_classes((JSONRenderer, XMLRenderer))
def getData(request):
    #read the file and parse to dataframe
    file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')
    vcf_file = read_vcf(file_path)

    #Logic for GET request
    paginator = pagination.PageNumberPagination()

    #case where client passes an id
    if 'id' in request.query_params:
        id = request.query_params['id']
        vcf_file = vcf_file.loc[vcf_file['ID'] == id]
        if vcf_file.empty:
            return Response(status=status.HTTP_404_NOT_FOUND)
    #Transform data to json, check if we have more than 10 items in order to paginate the response
    result = vcf_file.to_json(orient="records")
    parsed = json.loads(result)
    page = paginator.paginate_queryset(parsed, request)
    if page is not None:
        return paginator.get_paginated_response(page)
    return Response(parsed)
 


@api_view(['POST'])
@parser_classes([JSONParser])
@authentication_classes([PredefinedSecret])
@permission_classes([IsAuthenticated])
def postData(request, format=None):
    #read the file and parse to dataframe
    file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')

    #Logic for POST request
    #validate the data that has been sent. Return 403 for invalid data
    if validate_post_request(request.data):
        df = pd.DataFrame(request.data, index=[0])
        cols = ['CHROM', 'POS', 'ID', 'REF', 'ALT']
        df = df[cols]
        df.reset_index()
        df.to_csv(file_path, sep="\t", mode='a', index=False, header=False, quoting=csv.QUOTE_NONE)
        return Response(data="Row created", content_type="application/json", status=status.HTTP_201_CREATED)
    else: 
        return Response(data="Invalid content type", content_type="application/json", status=status.HTTP_403_FORBIDDEN)


@api_view(['PUT'])
@parser_classes([JSONParser])
@authentication_classes([PredefinedSecret])
@permission_classes([IsAuthenticated])
def putData(request):
    #read the file and parse to dataframe
    file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')
    vcf_file = read_original_vcf(file_path)
    #Logic for PUT request
    #validate the data that has been sent. Return 403 for invalid data
    if 'id' in request.query_params:
        #validate existance of id parameter
        if validate_post_request(request.data):
            row_id = request.query_params['id']
            #convert data to Dataframe and reorder columns
            data = pd.DataFrame(request.data, index=[0])
            cols = ['CHROM', 'POS', 'ID', 'REF', 'ALT']
            df = data[cols]
            
            #locate the rows in our original file
            rows_to_edit = vcf_file.loc[vcf_file['ID'] == row_id].copy()

            #if there are no rows to modify, return a 404 status code
            if rows_to_edit.empty:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                #replace the values of our file with the ones sent by the client

                #get the number of rows sent from the client
                no_of_rows = rows_to_edit.shape[0]
                
                #if the number of rows we need to edit is more that 1, then we need to reshape our second dataframe that contains our client data so that they both have an equal ammount of rows
                if no_of_rows > 1:
                    df = pd.concat([df]*no_of_rows)
                rows_to_edit[['CHROM', 'POS', 'ID', 'REF', 'ALT']] = df[['CHROM', 'POS', 'ID', 'REF', 'ALT']].values
                # #get the indexes of aformentioned rows
                index = vcf_file.index[vcf_file['ID'] == row_id]

                # #get file header
                header = get_vcf_header(file_path)
                #drop old rows and insert new ones with the correct data at the correct index
                vcf_file.drop(axis=0, index=index, inplace=True)
                vcf_file = pd.concat([vcf_file, rows_to_edit])
                vcf_file.sort_index(inplace=True)
                vcf_file.rename(columns={'CHROM': '#CHROM'})

                # #save to the vcf file. First add the header, then append the rest of the rows. (quoting=csv.QUOTE_NONE is added so that pd.to_csv doesn't add any unnecessary double quotes)
                header.to_csv(file_path, sep="\t", index=False, header=False, doublequote=False, quoting=csv.QUOTE_NONE)
                vcf_file.to_csv(file_path, sep="\t", mode='a', index=False, header=True, quoting=csv.QUOTE_NONE)
                return Response(data="Row(s) successfully edited", content_type="application/json", status=status.HTTP_200_OK)
        else: 
            return Response(data="Invalid content type", content_type="application/json", status=status.HTTP_403_FORBIDDEN)
    else:
        return Response(data="No id supplied from client", content_type="application/json", status=status.HTTP_403_FORBIDDEN)



@api_view(['DELETE'])
# @parser_classes([JSONParser])
@authentication_classes([PredefinedSecret])
@permission_classes([IsAuthenticated])
def deleteData(request):
       #read the file and parse to dataframe
    file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')
    vcf_file = read_original_vcf(file_path)
    
    #Logic for DELETE request
    #validate existance of id parameter else return 403
    if 'id' in request.query_params:
        #locate the rows we wish to delete by the given ID, and keep their indexes for the next step
        row_id = request.query_params['id']
        rows_to_delete = vcf_file.index[vcf_file["ID"] == row_id].copy()
        #if the Dataframe is empty then return 404 not found
        if rows_to_delete.empty:
            return Response(data="No rows found matching id", content_type="application/json", status=status.HTTP_404_NOT_FOUND)
        else:
            # convert the indexes of the found rows to a list, so we can pass it to the .drop method below
            rows_to_delete.to_list()
            vcf_file.drop(axis=0, index=rows_to_delete, inplace=True)
            vcf_file.reset_index()
            vcf_file.rename(columns={'CHROM': '#CHROM'})
            header = get_vcf_header(file_path)

            #save our files, first the header then append the columns
            header.to_csv(file_path, sep="\t", index=False, header=False, doublequote=False, quoting=csv.QUOTE_NONE)
            vcf_file.to_csv(file_path, sep="\t", mode='a', index=False, header=True, quoting=csv.QUOTE_NONE)
            return Response(data="Row(s) successfully Deleted", content_type="application/json", status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(data="No id supplied from client", content_type="application/json", status=status.HTTP_403_FORBIDDEN)




