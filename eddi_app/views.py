from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from eddi_app import models
from eddi_app.constants.constants import *
from eddi_app.constants.table_name import *
import datetime
from django.utils.timezone import make_aware
from django.contrib.auth.hashers import make_password, check_password
from .supplier_views import *
from uuid import uuid4




class UserSignupView(APIView):
    def post(self, request):
        if request.method == POST_METHOD:
            record_map = {
                EMAIL_ID: request.POST.get(EMAIL_ID),
                PASSWORD: make_password(request.POST.get(PASSWORD)),
                STATUS_ID:1
            }
            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[CREATED_BY] = 'admin'
            getattr(models,USERSIGNUP_TABLE).objects.update_or_create(**record_map)
            return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)

class GetUserDetails(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
            serializer = UserSignupSerializer(data)
            if serializer:
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = getattr(models,USERSIGNUP_TABLE).objects.all()
            serializer = UserSignupSerializer(data,many = True)
            if serializer:
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,uuid = None):
        if uuid:
            try:
                data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid,STATUS:1})
            except:
                return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
            record_map = {
                EMAIL_ID: request.FILES.get(EMAIL_ID,data.email_id),
                PASSWORD: request.POST.get(PASSWORD,data.password),
                IS_STUDENT : request.POST.get(IS_STUDENT,data.is_student),
                IS_SUPPLIER : request.POST.get(IS_SUPPLIER,data.is_supplier),
                IS_ADMIN : request.POST.get(IS_ADMIN,data.is_admin),
                IS_FIRST_TIME_LOGIN : request.POST.get(IS_FIRST_TIME_LOGIN,data.is_first_time_login),
                STATUS_ID:request.POST.get(STATUS_ID,data.status)
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
                data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid,STATUS:1})
            except:
                return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
            record_map = {
                EMAIL_ID: request.FILES.get(EMAIL_ID,data.email_id),
                PASSWORD: request.POST.get(PASSWORD,data.password),
                IS_STUDENT : request.POST.get(IS_STUDENT,data.is_student),
                IS_SUPPLIER : request.POST.get(IS_SUPPLIER,data.is_supplier),
                IS_ADMIN : request.POST.get(IS_ADMIN,data.is_admin),
                IS_FIRST_TIME_LOGIN : request.POST.get(IS_FIRST_TIME_LOGIN,data.is_first_time_login),
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
   

class UserLoginView(APIView):
    def post(self, request):
        email_id = request.POST.get(EMAIL_ID)
        password = request.POST.get(PASSWORD)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id,STATUS_ID:1})
        except:
            data = None
        serializer = UserSignupSerializer(data)
        if serializer and data:
            if check_password(password,data.password):
                if data.is_first_time_login:
                    return Response({STATUS: SUCCESS, IS_FIRST_TIME_LOGIN: True}, status=status.HTTP_200_OK)
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({STATUS: ERROR, DATA: "User Not Found"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    def post(self,request,uuid):

        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
            password = request.POST.get(PASSWORD)
        except:
            data = None
        try:
            if data:
                setattr(data,PASSWORD,make_password(password))
                setattr(data,MODIFIED_AT,make_aware(datetime.datetime.now()))
                setattr(data,MODIFIED_BY,'admin')
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Password Changed Successfull"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ex}, status=status.HTTP_400_BAD_REQUEST)



