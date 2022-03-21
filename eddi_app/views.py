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
        record_map = {}
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            EMAIL_ID: request.POST.get(EMAIL_ID),
            PASSWORD: make_password(request.POST.get(PASSWORD)),
            USER_TYPE_ID: 1,
            STATUS_ID:1
        }
        record_map[CREATED_AT] = make_aware(datetime.datetime.now())
        record_map[CREATED_BY] = 'admin'
        try:
            getattr(models,USERSIGNUP_TABLE).objects.update_or_create(**record_map)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "User Already Exists"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)

class GetUserDetails(APIView):
    def post(self, request):
        record_map = {}
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.filter(**{'user_type__user_type':request.POST.get('user_type')})
            if serializer := UserSignupSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "No data found"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)


    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
            if serializer := UserSignupSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = getattr(models,USERSIGNUP_TABLE).objects.all()
            if serializer := UserSignupSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,uuid = None):  # sourcery skip: class-extract-method
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            EMAIL_ID: request.FILES.get(EMAIL_ID,data.email_id),
            PASSWORD: request.POST.get(PASSWORD,data.password),
            USER_TYPE_ID: 2,
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

    def delete(self,request,uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            EMAIL_ID: request.FILES.get(EMAIL_ID,data.email_id),
            PASSWORD: request.POST.get(PASSWORD,data.password),
            USER_TYPE_ID: 2,
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
   

class UserLoginView(APIView):
    def post(self, request):
        email_id = request.POST.get(EMAIL_ID)
        password = request.POST.get(PASSWORD)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id,STATUS_ID:1})
            print(data.user_type)
        except:
            data = None
        serializer = UserSignupSerializer(data)
        # print(serializer, "serializerrrrrrrrrrr")
        if serializer and data:
            if not check_password(password, data.password):
                return Response({STATUS: ERROR, DATA: "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
            if data.is_first_time_login:
                return Response({STATUS: SUCCESS, IS_FIRST_TIME_LOGIN: True}, status=status.HTTP_200_OK)
            return Response({STATUS: SUCCESS, DATA: True,"user_type":str(data.user_type)}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "User Not Found"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    def post(self,request,uuid):
        # sourcery skip: extract-method, remove-unnecessary-else, swap-if-else-branches

        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
            password = request.POST.get(PASSWORD)
        except:
            data = None
        try:
            if data:
                setattr(data,PASSWORD,make_password(password))
                setattr(data,IS_FIRST_TIME_LOGIN,False)

                setattr(data,MODIFIED_AT,make_aware(datetime.datetime.now()))
                setattr(data,MODIFIED_BY,'admin')
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Password Changed Successfull"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ex}, status=status.HTTP_400_BAD_REQUEST)



class GetHomePageDetails(APIView): 
    def get(self, request):
            data = getattr(models,HOMEPAGECMS_TABLE).objects.latest('created_date_time')
            if serializer := HomePageCMSSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
       
class GetAboutUsPageDetails(APIView):
    def get(self, request):
            data = getattr(models,ABOUTUSCMS_TABLE).objects.latest('created_date_time')
            if serializer := AboutUsCMSSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class GetContactUsPageDetails(APIView):
    def get(self, request):
            data = getattr(models,CONTACTUSCMS_TABLE).objects.latest('created_date_time')
            if serializer := ContactUsCMSSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
class GetBlogDetails(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,BLOGDETAILS_TABLE).objects.get(**{UUID:uuid})
            if serializer := BlogDetailsSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = getattr(models,BLOGDETAILS_TABLE).objects.all()
            if serializer := BlogDetailsSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ContactFormView(APIView):
    def post(self, request):
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {
                FULLNAME : request.POST.get(FULLNAME),
                EMAIL_ID : request.POST.get(EMAIL_ID),
                PHONE_NUMBER : request.POST.get(PHONE_NUMBER),
                MESSAGE : request.POST.get(MESSAGE)
            }

            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[CREATED_BY] = 'admin'
            try:
                getattr(models,CONTACT_FORM_TABLE).objects.update_or_create(**record_map)
            except:
                return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)