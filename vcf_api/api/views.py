import json
import os
from . import read_file
from pathlib import Path
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework import pagination
#required for returning xml
from rest_framework_xml.renderers import XMLRenderer
import pandas as pd
from django.http import Http404
from .validation import validate_post_request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .authentication import PredefinedSecret



#TODO add exception handling 
@api_view(['GET'])
@renderer_classes((JSONRenderer, XMLRenderer))
def getData(request):
    #read the file and parse to dataframe
    file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')
    parsed_file = read_file.read_vcf(file_path)

    #Logic for GET request
    paginator = pagination.PageNumberPagination()
    if 'id' in request.query_params:
        id = request.query_params['id']
        parsed_file = parsed_file.loc[parsed_file['ID'] == id]
        if parsed_file.empty:
            raise Http404("Not Found")
    result = parsed_file.to_json(orient="records")
    parsed = json.loads(result)
    page = paginator.paginate_queryset(parsed, request)
    if page is not None:
        return paginator.get_paginated_response(page)
    return Response(parsed)
 


@api_view(['POST'])
@renderer_classes((JSONRenderer, XMLRenderer))
@authentication_classes([PredefinedSecret])
@permission_classes([IsAuthenticated])
def postData(request):
    #read the file and parse to dataframe
    file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')
    # parsed_file = read_file.read_vcf(file_path)

    #Logic for POST request
    if validate_post_request(request.data):
        df = pd.DataFrame(request.data, index=[0])
        df.to_csv(file_path, sep="\t", mode='a', index=False, header=False)
        return Response(status=status.HTTP_201_CREATED)
    else: 
        return Response(status=status.HTTP_403_FORBIDDEN)
