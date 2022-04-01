from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from eddi_app import models
from eddi_app.constants.constants import *
from eddi_app.constants.table_name import *
import datetime
from django.utils.timezone import make_aware
from uuid import uuid4
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny



class AddCourseView(APIView):
    def post(self, request):
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)

        # if request.POST.get(COURSE_FOR_ORGANIZATION) == 'true':
        
        #     test_str = data.supplier.email_id
        #     res = test_str.split('@')[1]
        #     print(res)
        try:
            category_id = getattr(models,COURSE_CATEGORY_TABLE).objects.only(ID).get(**{CATEGORY_NAME:request.POST.get(COURSE_CATEGORY_ID,None)})
            sub_category_id = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.only(ID).get(**{SUBCATEGORY_NAME:request.POST.get(SUBCATEGORY_NAME_ID,None)})
            course_type_id = getattr(models,COURSE_TYPE_TABLE).objects.only(ID).get(**{TYPE_NAME:request.POST.get(COURSE_TYPE_ID,None)})
            fee_type_id = getattr(models,FEE_TYPE_TABLE).objects.only(ID).get(**{FEE_TYPE_NAME :request.POST.get(FEE_TYPE_ID,None)})
            course_level_id = getattr(models,COURSE_LEVEL_TABLE).objects.only(ID).get(**{LEVEL_NAME : request.POST.get(COURSE_LEVEL_ID,None)})
        except Exception as ex:
            return Response({STATUS:ERROR, DATA: "Error Getting Data"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            SUPPLIER_ID: request.POST.get(SUPPLIER_ID,None),
            COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,None),
            COURSE_NAME: request.POST.get(COURSE_NAME,None),
            COURSE_LEVEL_ID : course_level_id.id,
            COURSE_LENGTH : request.POST.get(COURSE_LENGTH,None),
            COURSE_CATEGORY_ID :category_id.id ,
            COURSE_SUBCATEGORY_ID : sub_category_id.id,
            COURSE_TYPE_ID : course_type_id.id,
            FEE_TYPE_ID: fee_type_id.id,
            COURSE_FOR_ORGANIZATION:eval(request.POST.get(COURSE_FOR_ORGANIZATION).title()),
            # ORGANIZATION_DOMAIN:res,
            COURSE_LANGUAGE:request.POST.get(COURSE_LANGUAGE),
            COURSE_CHECKOUT_LINK: request.POST.get(COURSE_CHECKOUT_LINK,None),
            COURSE_PRICE: request.POST.get(COURSE_PRICE,None),
            ADDITIONAL_INFORMATION: request.POST.get(ADDITIONAL_INFORMATION,None),
            ORGANIZATION_LOCATION: request.POST.get(ORGANIZATION_LOCATION,None),
            SUB_AREA:request.POST.get(SUB_AREA,None),
            STATUS_ID:1
        }
        record_map[CREATED_AT] = make_aware(datetime.datetime.now())
        record_map[CREATED_BY] = 'admin'
        getattr(models,COURSEDETAILS_TABLE).objects.update_or_create(**record_map)
        return Response({STATUS: SUCCESS, DATA: "Course Created successfully"}, status=status.HTTP_200_OK)


class AddSubCategoryView(APIView):
    def post(self, request):
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:    
            category_id = getattr(models,COURSE_CATEGORY_TABLE).objects.get(**{CATEGORY_NAME:request.POST.get(CATEGORY_NAME_ID,None)})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "error Getting Category Name"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            SUPPLIER_ID:request.POST.get(SUPPLIER_ID,None),
            CATEGORY_NAME_ID: category_id.id,
            SUBCATEGORY_NAME: request.POST.get(SUBCATEGORY_NAME,None),
            SUBCATEGORY_IMAGE : request.FILES.get(SUBCATEGORY_IMAGE,None),
            STATUS_ID:1
        }
        record_map[CREATED_AT] = make_aware(datetime.datetime.now())
        record_map[CREATED_BY] = 'admin'
        getattr(models,COURSE_SUBCATEGORY_TABLE).objects.update_or_create(**record_map)
        return Response({STATUS: SUCCESS, DATA: "Sub Category Created successfully"}, status=status.HTTP_200_OK)

class GetCategoryDetails(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,COURSE_CATEGORY_TABLE).objects.get(**{UUID:uuid})
            if serializer := CategoryDetailsSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = getattr(models,COURSE_CATEGORY_TABLE).objects.all()
            if serializer := CategoryDetailsSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetSubCategoryDetails(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.get(**{UUID:uuid})
            if serializer := SubCategoryDetailsSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.all()
            if serializer := SubCategoryDetailsSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            dataa = getattr(models,COURSE_CATEGORY_TABLE).objects.get(**{CATEGORY_NAME:request.POST.get(CATEGORY_NAME_ID)})
        except Exception as ex:
            print(ex)

            return Response({STATUS: ERROR, DATA: "Category Error"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            CATEGORY_NAME_ID: request.POST.get(dataa.id,data.category_name_id),
            SUBCATEGORY_NAME: request.POST.get(SUBCATEGORY_NAME,data.subcategory_name),
            SUBCATEGORY_IMAGE : request.FILES.get(SUBCATEGORY_IMAGE,data.subcategory_image),
            STATUS_ID:1
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data Succesfully Edited"}, status=status.HTTP_200_OK)

    def delete(self,request,uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            CATEGORY_NAME_ID: request.POST.get(CATEGORY_NAME,data.category_name_id),
            SUBCATEGORY_NAME: request.POST.get(SUBCATEGORY_NAME,data.subcategory_name),
            SUBCATEGORY_IMAGE : request.FILES.get(SUBCATEGORY_IMAGE,data.subcategory_image),
            STATUS_ID:request.POST.get(STATUS,data.status)
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data Succesfully Deleted"}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class GetCourseDetails(APIView):
    res = None
    domain_data = None
    def get(self, request,uuid = None):
        res = None
        if uuid:
            data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid})
            if serializer := CourseDetailsSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if request.headers.get('email') != 'undefined':
                data = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS:1}).order_by('-organization_domain')
            else:

                data = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS:1}).exclude(**{'course_for_organization':True})
            if serializer := CourseDetailsSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,uuid = None):
        res = None
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category_id = getattr(models,COURSE_CATEGORY_TABLE).objects.only(ID).get(**{CATEGORY_NAME:request.POST.get(COURSE_CATEGORY_ID,None)})
            sub_category_id = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.only(ID).get(**{SUBCATEGORY_NAME:request.POST.get(SUBCATEGORY_NAME_ID,None)})
            course_type_id = getattr(models,COURSE_TYPE_TABLE).objects.only(ID).get(**{TYPE_NAME:request.POST.get(COURSE_TYPE_ID,None)})
            fee_type_id = getattr(models,FEE_TYPE_TABLE).objects.only(ID).get(**{FEE_TYPE_NAME :request.POST.get(FEE_TYPE_ID,None)})
            course_level_id = getattr(models,COURSE_LEVEL_TABLE).objects.only(ID).get(**{LEVEL_NAME : request.POST.get(COURSE_LEVEL_ID,None)})
        except Exception as ex:
            return Response({STATUS:ERROR, DATA: "Error Getting Data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)

        if request.POST.get(COURSE_FOR_ORGANIZATION) == 'true':
        
            test_str = data.supplier.email_id
            res = test_str.split('@')[1]
            print(res)

        record_map = {
            COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,data.course_image),
            COURSE_NAME: request.POST.get(COURSE_NAME,data.course_name),
            COURSE_LEVEL_ID : course_level_id.id,
            COURSE_LENGTH : request.POST.get(COURSE_LENGTH,data.course_length),
            COURSE_CATEGORY_ID : category_id.id,
            COURSE_SUBCATEGORY_ID: sub_category_id.id,
            COURSE_TYPE_ID : course_type_id.id,
            COURSE_FOR_ORGANIZATION:eval(request.POST.get(COURSE_FOR_ORGANIZATION).title()),
            COURSE_LANGUAGE:request.POST.get(COURSE_LANGUAGE),
            COURSE_CHECKOUT_LINK: request.POST.get(COURSE_CHECKOUT_LINK,None),
            ORGANIZATION_DOMAIN:res,
            FEE_TYPE_ID: fee_type_id.id,
            COURSE_PRICE: request.POST.get(COURSE_PRICE,data.course_price),
            ADDITIONAL_INFORMATION: request.POST.get(ADDITIONAL_INFORMATION,data.additional_information),
            STATUS_ID:1,
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data Succesfully Edited"}, status=status.HTTP_200_OK)

    def delete(self,request,uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,data.course_image),
            COURSE_NAME: request.POST.get(COURSE_NAME,data.course_name),
            COURSE_LEVEL_ID : request.POST.get(COURSE_LEVEL_ID,data.course_level_id),
            COURSE_LENGTH : request.POST.get(COURSE_LENGTH,data.course_length),
            COURSE_CATEGORY_ID : request.POST.get(COURSE_CATEGORY_ID,data.course_category_id),
            COURSE_TYPE_ID : request.POST.get(COURSE_TYPE_ID,data.course_type_id),
            FEE_TYPE_ID: request.POST.get(FEE_TYPE_ID,data.fee_type_id),
            COURSE_PRICE: request.POST.get(COURSE_PRICE,data.course_price),
            ADDITIONAL_INFORMATION: request.POST.get(ADDITIONAL_INFORMATION,data.additional_information),
            STATUS_ID:2
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data Succesfully Deleted"}, status=status.HTTP_200_OK)
    
