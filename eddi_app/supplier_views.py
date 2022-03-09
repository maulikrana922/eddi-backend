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



class AddCourseView(APIView):
    def post(self, request):
        if request.method == POST_METHOD:
            record_map = {
                COURSE_IMAGE: request.FILES[COURSE_IMAGE],
                COURSE_NAME: request.POST.get(COURSE_NAME,None),
                COURSE_LEVEL_ID : request.POST.get(COURSE_LEVEL_ID,None),
                COURSE_LENGTH : request.POST.get(COURSE_LENGTH,None),
                COURSE_CATEGORY_ID : request.POST.get(COURSE_CATEGORY_ID,None),
                COURSE_TYPE_ID : request.POST.get(COURSE_TYPE_ID,None),
                FEE_TYPE_ID: request.POST.get(FEE_TYPE_ID,None),
                COURSE_PRICE: request.POST.get(COURSE_PRICE,None),
                ADDITIONAL_INFORMATION: request.POST.get(ADDITIONAL_INFORMATION,None),
                STATUS_ID:1
            }
            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[CREATED_BY] = 'admin'
            getattr(models,COURSEDETAILS_TABLE).objects.update_or_create(**record_map)
            return Response({STATUS: SUCCESS, DATA: "Course Created successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)


class AddSubCategoryView(APIView):
    def post(self, request):
        if request.method == POST_METHOD:
            record_map = {
                CATEGORY_NAME_ID: request.POST.get(CATEGORY_NAME,None),
                SUBCATEGORY_NAME: request.POST.get(SUBCATEGORY_NAME,None),
                SUBCATEGORY_IMAGE : request.FILES.get(SUBCATEGORY_IMAGE,None),
                STATUS_ID:1
            }
            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[CREATED_BY] = 'admin'
            getattr(models,COURSE_SUBCATEGORY_TABLE).objects.update_or_create(**record_map)
            return Response({STATUS: SUCCESS, DATA: "Sub Category Created successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)

class GetCategoryDetails(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,COURSE_CATEGORY_TABLE).objects.get(**{UUID:uuid})
            serializer = CategoryDetailsSerializer(data)
            if serializer:
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = getattr(models,COURSE_CATEGORY_TABLE).objects.all()
            serializer = CategoryDetailsSerializer(data,many = True)
            if serializer:
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetSubCategoryDetails(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.get(**{UUID:uuid})
            serializer = SubCategoryDetailsSerializer(data)
            if serializer:
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.all()
            serializer = SubCategoryDetailsSerializer(data,many = True)
            if serializer:
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,uuid = None):
        if uuid:
            try:
                data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.get(**{UUID:uuid,STATUS:1})
            except:
                return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
            record_map = {
                CATEGORY_NAME_ID: request.POST.get(CATEGORY_NAME,data.category_name_id),
                SUBCATEGORY_NAME: request.POST.get(SUBCATEGORY_NAME,data.subcategory_name),
                SUBCATEGORY_IMAGE : request.FILES.get(SUBCATEGORY_IMAGE,data.subcategory_image.url),
                STATUS_ID:request.POST.get(STATUS,data.status)
            }
            record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
            record_map[MODIFIED_BY] = 'admin'
            record_map[UUID] = uuid4()
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()
            return Response({STATUS: SUCCESS, DATA: "Data Succesfully Edited"}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,uuid = None):
        if uuid:
            try:
                data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid,STATUS:1})
            except:
                return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
            record_map = {
                COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,data.course_image.url),
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
        else:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)


class GetCourseDetails(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid})
            serializer = CourseDetailsSerializer(data)
            if serializer:
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = getattr(models,COURSEDETAILS_TABLE).objects.all()
            serializer = CourseDetailsSerializer(data,many = True)
            if serializer:
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,uuid = None):
        if uuid:
            try:
                data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid,STATUS:1})
            except:
                return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
            record_map = {
                COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,data.course_image.url),
                COURSE_NAME: request.POST.get(COURSE_NAME,data.course_name),
                COURSE_LEVEL_ID : request.POST.get(COURSE_LEVEL_ID,data.course_level_id),
                COURSE_LENGTH : request.POST.get(COURSE_LENGTH,data.course_length),
                COURSE_CATEGORY_ID : request.POST.get(COURSE_CATEGORY_ID,data.course_category_id),
                COURSE_TYPE_ID : request.POST.get(COURSE_TYPE_ID,data.course_type_id),
                FEE_TYPE_ID: request.POST.get(FEE_TYPE_ID,data.fee_type_id),
                COURSE_PRICE: request.POST.get(COURSE_PRICE,data.course_price),
                ADDITIONAL_INFORMATION: request.POST.get(ADDITIONAL_INFORMATION,data.additional_information),
                STATUS_ID:request.POST.get(STATUS,data.status),
            }
            record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
            record_map[MODIFIED_BY] = 'admin'
            record_map[UUID] = uuid4()
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()
            return Response({STATUS: SUCCESS, DATA: "Data Succesfully Edited"}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,uuid = None):
        if uuid:
            try:
                data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid,STATUS:1})
            except:
                return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
            record_map = {
                COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,data.course_image.url),
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
        else:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)