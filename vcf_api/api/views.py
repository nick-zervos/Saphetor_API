import json
import os
from .read_file import read_vcf
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
        df.to_csv(file_path, sep="\t", mode='a', index=False, header=False)
        return Response(data="Row created", content_type="application/json", status=status.HTTP_201_CREATED)
    else: 
        return Response(data="Invalid content type", content_type="application/json", status=status.HTTP_403_FORBIDDEN)

