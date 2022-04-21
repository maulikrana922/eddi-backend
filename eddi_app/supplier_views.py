from calendar import TUESDAY
from posixpath import split
from select import select
import json
from typing import final
from wsgiref.handlers import read_environ
from pytz import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from .serializers import *
from datetime import timezone
from eddi_app import models
from eddi_app.constants.constants import *
from eddi_app.constants.table_name import *
import datetime
from django.utils.timezone import make_aware
from uuid import uuid4
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db.models import Q 
from datetime import timedelta
from time import strptime
from dateutil.relativedelta import *
from collections import deque

@permission_classes([AllowAny])
def get_user_email_by_token(request):
    try:
        token_data = request.headers.get('Authorization')
        token = token_data.split()[1]
    except:
        return Response({STATUS:"Auth Token not found"})

    try:
        data = getattr(models,TOKEN_TABLE).objects.get(key = token)
        return data.user.email_id
    except Exception as ex:
        print(ex)
        data = None
        return data

class AddCourseView(APIView):
    def post(self, request):
        res = None
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)

        email_id = get_user_email_by_token(request)
        course_organization = None

        if request.POST.get(COURSE_FOR_ORGANIZATION) == 'true':
            course_organization = True
            test_str = email_id
            res = test_str.split('@')[1]
            print(res)
        else:
            course_organization = False
        try:    
            supplier_id = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "error Getting Suppier Details"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            category_id = getattr(models,COURSE_CATEGORY_TABLE).objects.only(ID).get(**{CATEGORY_NAME:request.POST.get(COURSE_CATEGORY_ID,None)})
            sub_category_id = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.only(ID).get(**{SUBCATEGORY_NAME:request.POST.get(SUBCATEGORY_NAME_ID,None)})
            course_type_id = getattr(models,COURSE_TYPE_TABLE).objects.only(ID).get(**{TYPE_NAME:request.POST.get(COURSE_TYPE_ID,None)})
            fee_type_id = getattr(models,FEE_TYPE_TABLE).objects.only(ID).get(**{FEE_TYPE_NAME :request.POST.get(FEE_TYPE_ID,None)})
            course_level_id = getattr(models,COURSE_LEVEL_TABLE).objects.only(ID).get(**{LEVEL_NAME : request.POST.get(COURSE_LEVEL_ID,None)})
        except Exception as ex:
            print(ex,"exxxxxxxxxxxxxxxx")
            return Response({STATUS:ERROR, DATA: "Error Getting Data"}, status=status.HTTP_400_BAD_REQUEST)
        print(request.POST.get("organization_location"), "locationnonononononon")
        try:
            record_map = {
            SUPPLIER_ID: supplier_id.id,
            COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,None),
            COURSE_NAME: request.POST.get(COURSE_NAME,None),
            # "course_start_date": request.POST.get("course_start_date",None),
            COURSE_LEVEL_ID : course_level_id.id,
            COURSE_LENGTH : request.POST.get(COURSE_LENGTH,None),
            COURSE_CATEGORY_ID :category_id.id ,
            COURSE_SUBCATEGORY_ID : sub_category_id.id,
            COURSE_TYPE_ID : course_type_id.id,
            FEE_TYPE_ID: fee_type_id.id,
            COURSE_FOR_ORGANIZATION:course_organization,
            ORGANIZATION_DOMAIN:res,
            COURSE_LANGUAGE:request.POST.get(COURSE_LANGUAGE),
            COURSE_CHECKOUT_LINK: request.POST.get(COURSE_CHECKOUT_LINK,None),
            COURSE_PRICE: request.POST.get(COURSE_PRICE,None),
            ADDITIONAL_INFORMATION: request.POST.get(ADDITIONAL_INFORMATION,None),
            ORGANIZATION_LOCATION: request.POST.get(ORGANIZATION_LOCATION,None),
            SUB_AREA:request.POST.get(SUB_AREA,None),
            IS_APPROVED_ID : 2,
            STATUS_ID:1
            }
            if request.POST.get(COURSE_STARTING_DATE) == "":
                record_map[COURSE_STARTING_DATE] = None
            else:
                record_map[COURSE_STARTING_DATE] = request.POST.get(COURSE_STARTING_DATE)
            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[CREATED_BY] = 'admin'
            getattr(models,COURSEDETAILS_TABLE).objects.update_or_create(**record_map)
            return Response({STATUS: SUCCESS, DATA: "Course Created successfully"}, status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex, "exxxxx")
            return Response({STATUS:ERROR, DATA: "Error Saving in record map"}, status=status.HTTP_400_BAD_REQUEST)



class AddSubCategoryView(APIView):
    def post(self, request):
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)
        email_id = get_user_email_by_token(request)
        try:    
            supplier_id = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "error Getting Suppier Details"}, status=status.HTTP_400_BAD_REQUEST)
        try:    
            category_id = getattr(models,COURSE_CATEGORY_TABLE).objects.get(**{CATEGORY_NAME:request.POST.get(CATEGORY_NAME_ID,None)})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "error Getting Category Name"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            SUPPLIER_ID:supplier_id.id,
            CATEGORY_NAME_ID: category_id.id,
            SUBCATEGORY_NAME: request.POST.get(SUBCATEGORY_NAME,None),
            SUBCATEGORY_IMAGE : request.FILES.get(SUBCATEGORY_IMAGE,None),
            IS_APPROVED_ID : 2,
            STATUS_ID:1
        }
        record_map[CREATED_AT] = make_aware(datetime.datetime.now())
        record_map[CREATED_BY] = 'admin'
        getattr(models,COURSE_SUBCATEGORY_TABLE).objects.update_or_create(**record_map)
        return Response({STATUS: SUCCESS, DATA: "Sub Category Created successfully"}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
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
            email_id = get_user_email_by_token(request)
            try:
                user_type_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type
            except Exception:
                user_type_data = None
            if user_type_data:
                if user_type_data == ADMIN_S:
                    data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.all().order_by("-created_date_time")
                else:
                    data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.filter(**{'supplier__email_id':email_id}).order_by("-created_date_time")
            if serializer := SubCategoryDetailsSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,uuid = None):
        email_id =  get_user_email_by_token(request)
        try:
            user_type_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type
        except Exception:
            user_type_data = None
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.get(**{UUID:uuid})
        except Exception as ex:
            print(ex, "ex")
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            dataa = getattr(models,COURSE_CATEGORY_TABLE).objects.get(**{CATEGORY_NAME:request.POST.get(CATEGORY_NAME_ID,data.category_name.category_name)})
        except Exception as ex:
            print(ex, "exxx")
            return Response({STATUS: ERROR, DATA: "Category Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {

            CATEGORY_NAME_ID: dataa.id,
            SUBCATEGORY_NAME: request.POST.get(SUBCATEGORY_NAME,data.subcategory_name),
            SUBCATEGORY_IMAGE : request.FILES.get(SUBCATEGORY_IMAGE,data.subcategory_image),
         }
            print(record_map, "recordddddd")
        except Exception as ex:
            print(ex, "exxxxx")
        if user_type_data:
            if user_type_data == ADMIN_S:
                if request.POST.get(STATUS):
                    if request.POST.get(STATUS) == "Active":
                        record_map[STATUS_ID] = 1
                    else:
                        try:
                            data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{COURSE_CATEGORY:data.category_name})
                        except Exception as ex:
                            print(ex, "exxxx")
                            data1 = None
                        if data1.exists():
                            return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Category"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            record_map[STATUS_ID] = 2
                else:
                    record_map[STATUS] = data.status
                    
                if request.POST.get(APPROVAL_STATUS):
                    if request.POST.get(APPROVAL_STATUS) == "Approved":
                        record_map[IS_APPROVED_ID] = 1
                    if request.POST.get(APPROVAL_STATUS) == "Pending":
                        try:
                            data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{COURSE_CATEGORY:data.category_name})
                        except Exception as ex:
                            print(ex, "exxxx")
                            data1 = None
                        if data1.exists():
                            return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Category"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            record_map[IS_APPROVED_ID] = 2
                    if request.POST.get(APPROVAL_STATUS) == "Rejected":
                        try:
                            data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{COURSE_CATEGORY:data.category_name})
                        except Exception as ex:
                            print(ex, "exxxx")
                            data1 = None
                        if data1.exists():
                            return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Category"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            record_map[IS_APPROVED_ID] = 3
                else:
                    record_map[IS_APPROVED] = data.is_approved

            elif user_type_data == SUPPLIER_S:
                if request.POST.get(STATUS):
                    if request.POST.get(STATUS) == "Active":
                        record_map[STATUS_ID] = 1
                    else:
                        try:
                            data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{COURSE_CATEGORY:data.category_name})
                        except Exception as ex:
                            print(ex, "exxxx")
                            data1 = None
                        if data1.exists():
                            return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Course"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            record_map[STATUS_ID] = 2
                else:
                    record_map[STATUS] = data.status
                    record_map[IS_APPROVED_ID] = 2

        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        record_map[UUID] = uuid4()
        print(record_map, "recorddddd")
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
            STATUS_ID:2
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data Succesfully Deleted"}, status=status.HTTP_200_OK)

class GetCourseDetails(APIView):
    res = None
    domain_data = None
    email_id = None
    fav_data = None
    fav_dataa = None
    
    def get(self, request,uuid = None):
        res = None
        fav_dataa = None
        course_name = None
        course_data = None
        individuals = None
        if uuid:
            email_id = get_user_email_by_token(request)
            try:
                course_data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid})
            except:
                course_data = None
            try:
                fav_data = getattr(models,FAVOURITE_COURSE_TABLE).objects.filter(**{COURSE_NAME:course_data.course_name}).get(**{EMAIL_ID:email_id})
                fav_dataa = fav_data.is_favourite
            except Exception as ex:
                fav_data = None
                fav_dataa = None

            try:
                individuals = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{COURSE_NAME:course_data.course_name, STATUS:"Success"})
                # lerner_count = getattr(models,USER_PAYMENT_DETAIL).objects.filter(course_name = course_data.course_name, status="Success").count()
                lerner_count = len(individuals)
              
            except Exception as e:
                individuals = None
            try:
                var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, COURSE_NAME:course_data.course_name, STATUS:"Success"})
            except Exception as ex:
                var = None
            var1 = True if var is not None else False

            if serializer := CourseDetailsSerializer(course_data):
                if serializer1 := CourseEnrollSerializer(individuals, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data,ENROLLED: serializer1.data,'is_favoutite':fav_dataa, "learners_count": lerner_count, "is_enrolled": var1}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors,ENROLLED: "No Enrolled User"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            email_id =  get_user_email_by_token(request)
            if email_id:
                if getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == SUPPLIER_S:
                    try:
                        data_s = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{'supplier__email_id':email_id}).order_by("-created_date_time")
                    except Exception as ex:
                        return Response({STATUS: ERROR, DATA: "Error in getting supplier data"}, status=status.HTTP_400_BAD_REQUEST)
                    print("insidesupplier")
                    if serializer := CourseDetailsSerializer(data_s,many=True):
                        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

                elif getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == ADMIN_S:
                    try:
                        data_a = getattr(models,COURSEDETAILS_TABLE).objects.all().order_by("-created_date_time")
                    except Exception as ex:
                        return Response({STATUS: ERROR, DATA: "Error in getting Admin data"}, status=status.HTTP_400_BAD_REQUEST)
                    print("insideadmin")

                    if serializer := CourseDetailsSerializer(data_a,many=True):
                        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

                else:
                    try:
                        cat = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                        try:
                            a = cat.course_category.split(",")
                        except Exception as ex:
                            a = cat.course_category.split()
                        print(a)
                    except Exception as ex:
                        print(ex, "exxxxxxxxx")

                    organization_domain = email_id.split('@')[1]

                    data_category = getattr(models,COURSEDETAILS_TABLE).objects.filter(Q(organization_domain = organization_domain) | Q(course_category__category_name__in = a)).filter(**{STATUS_ID:1, IS_APPROVED_ID:1}).order_by("-organization_domain")

                    data_category_list = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1}).filter(Q(organization_domain = organization_domain) | Q(course_category__category_name__in = a)).values_list(COURSE_NAME, flat=True)

                    data_all = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1}).exclude(course_name__in = data_category_list).order_by("-organization_domain")
                if serializer := CourseDetailsSerializer(data_category,many=True):
                    if serializer_all := CourseDetailsSerializer(data_all, many=True):
                        return Response({STATUS: SUCCESS, DATA: serializer.data, "all_data": serializer_all.data}, status=status.HTTP_200_OK)
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                   
            else:
                data_s = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS:1}).exclude(**{'course_for_organization':True})
                
           
            if serializer := CourseDetailsSerializer(data_s):
                return Response({STATUS: SUCCESS, DATA: data_s}, status=status.HTTP_200_OK)

                # if serializer1 := CourseEnrollSerializer(individuals, many=True):
                #     return Response({STATUS: SUCCESS, DATA: serializer.data,ENROLLED: serializer1.data,'is_favoutite':fav_dataa}, status=status.HTTP_200_OK)
                # else:
                #     return Response({STATUS: SUCCESS, DATA: serializer.data,ENROLLED: "No Enrolled User",'is_favoutite':fav_dataa}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
       

    def put(self,request,uuid = None):
        email_id =  get_user_email_by_token(request)
        try:
            user_type_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type
        except Exception:
            user_type_data = None
            
        res = None
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category_id = getattr(models,COURSE_CATEGORY_TABLE).objects.only(ID).get(**{CATEGORY_NAME:request.POST.get(COURSE_CATEGORY_ID,data.course_category.category_name)})

            sub_category_id = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.only(ID).get(**{SUBCATEGORY_NAME:request.POST.get(SUBCATEGORY_NAME_ID,data.course_subcategory.subcategory_name)})

            course_type_id = getattr(models,COURSE_TYPE_TABLE).objects.only(ID).get(**{TYPE_NAME:request.POST.get(COURSE_TYPE_ID,data.course_type.type_name)})

            fee_type_id = getattr(models,FEE_TYPE_TABLE).objects.only(ID).get(**{FEE_TYPE_NAME :request.POST.get(FEE_TYPE_ID,data.fee_type.fee_type_name)})

            course_level_id = getattr(models,COURSE_LEVEL_TABLE).objects.only(ID).get(**{LEVEL_NAME : request.POST.get(COURSE_LEVEL_ID,data.course_level.level_name)})
        except Exception as ex:
            print(ex, "ex")
            return Response({STATUS:ERROR, DATA: "Error Getting Data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {
            COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,data.course_image),
            COURSE_NAME: request.POST.get(COURSE_NAME,data.course_name),
            COURSE_LEVEL_ID : course_level_id.id,
            COURSE_LENGTH : request.POST.get(COURSE_LENGTH,data.course_length),
            COURSE_CATEGORY_ID : category_id.id,
            COURSE_SUBCATEGORY_ID: sub_category_id.id,
            COURSE_TYPE_ID : course_type_id.id,
            COURSE_LANGUAGE:request.POST.get(COURSE_LANGUAGE,data.course_language),
            ORGANIZATION_LOCATION: request.POST.get(ORGANIZATION_LOCATION,data.organization_location),
            COURSE_CHECKOUT_LINK: request.POST.get(COURSE_CHECKOUT_LINK,data.course_checkout_link),
            FEE_TYPE_ID: fee_type_id.id,
            SUB_AREA:request.POST.get(SUB_AREA,data.sub_area),
            COURSE_PRICE: request.POST.get(COURSE_PRICE,data.course_price),
            ADDITIONAL_INFORMATION: request.POST.get(ADDITIONAL_INFORMATION,data.additional_information),
        }
            if request.POST.get(COURSE_STARTING_DATE) == "":
                record_map[COURSE_STARTING_DATE] = None
            else:
                record_map[COURSE_STARTING_DATE] = request.POST.get(COURSE_STARTING_DATE,data.course_starting_date)
            if request.POST.get(COURSE_FOR_ORGANIZATION):
                if request.POST.get(COURSE_FOR_ORGANIZATION) == 'true':
                    record_map[COURSE_FOR_ORGANIZATION] = json.loads(request.POST.get(COURSE_FOR_ORGANIZATION))
                    test_str = data.supplier.email_id
                    res = test_str.split('@')[1]
                    record_map[ORGANIZATION_DOMAIN] = res
                    print(res)
                elif request.POST.get(COURSE_FOR_ORGANIZATION) == 'false':
                    record_map[COURSE_FOR_ORGANIZATION] = json.loads(request.POST.get(COURSE_FOR_ORGANIZATION))
                    record_map[ORGANIZATION_DOMAIN] = None
            else:
                record_map[COURSE_FOR_ORGANIZATION] = data.course_for_organization
                res = data.organization_domain

            if user_type_data:
                if user_type_data == ADMIN_S:
                    if request.POST.get(STATUS):
                        if request.POST.get(STATUS) == "Active":
                            record_map[STATUS_ID] = 1
                        else:
                            try:
                                data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__course_name":data.course_name})
                            except Exception as ex:
                                print(ex, "exxxx")
                                data1 = None
                            if data1.exists():
                                return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Course"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                record_map[STATUS_ID] = 2
                                try:
                                    print("INNER")
                                    html_path = INACTIVE_COURSE
                                    context_data = {"course_name":request.POST.get(COURSE_NAME,data.course_name)}
                                    email_html_template = get_template(html_path).render(context_data)
                                    email_from = settings.EMAIL_HOST_USER
                                    recipient_list = (data.supplier.email_id,)
                                    email_msg = EmailMessage('Welcome to Eddi',email_html_template,email_from,recipient_list)
                                    email_msg.content_subtype = 'html'
                                    email_msg.send(fail_silently=False)
                                    print("TRUE")
                                except Exception as ex:
                                    print(ex, "exexexexexe")
                    else:
                        record_map[STATUS] = data.status
                        
                    if request.POST.get(APPROVAL_STATUS):
                        if request.POST.get(APPROVAL_STATUS) == "Approved":
                            record_map[IS_APPROVED_ID] = 1
                            print("INNER")
                            html_path = APPROVE_COURSE_HTML
                            context_data = {"course_name":request.POST.get(COURSE_NAME,data.course_name)}
                            email_html_template = get_template(html_path).render(context_data)
                            email_from = settings.EMAIL_HOST_USER
                            recipient_list = (data.supplier.email_id,)
                            email_msg = EmailMessage('Welcome to Eddi',email_html_template,email_from,recipient_list)
                            email_msg.content_subtype = 'html'
                            email_msg.send(fail_silently=False)
                            print("TRUE")

                        if request.POST.get(APPROVAL_STATUS) == "Pending":
                            try:
                                data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__course_name":data.course_name})
                            except Exception as ex:
                                print(ex, "exxxx")
                                data1 = None
                            if data1.exists():
                                return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Course"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                record_map[IS_APPROVED_ID] = 2
                        if request.POST.get(APPROVAL_STATUS) == "Rejected":
                            try:
                                data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__course_name":data.course_name})
                            except Exception as ex:
                                print(ex, "exxxx")
                                data1 = None
                            if data1.exists():
                                return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Course"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                record_map[IS_APPROVED_ID] = 3
                    else:
                        record_map[IS_APPROVED] = data.is_approved

                elif user_type_data == SUPPLIER_S:
                    if request.POST.get(STATUS):
                        if request.POST.get(STATUS) == "Active":
                            record_map[STATUS_ID] = 1
                        else:
                            try:
                                data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__course_name":data.course_name})
                            except Exception as ex:
                                print(ex, "exxxx")
                                data1 = None
                            if data1.exists():
                                return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Course"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                record_map[STATUS_ID] = 2
                    else:
                        record_map[STATUS] = data.status
                        record_map[IS_APPROVED_ID] = 2


                record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
                record_map[MODIFIED_BY] = 'admin'
                record_map[UUID] = uuid4()
                print(record_map, "recordddddddddd")
                for key,value in record_map.items():
                    setattr(data,key,value)
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Data Succesfully Edited"}, status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex, "exxxxxxxxxxxxxxx")
            return Response({STATUS: ERROR, DATA: "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request,uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except Exception:
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
    


class SupplierDashboardView(APIView):
    def post(self, request,uuid = None):
        supplier_email = get_user_email_by_token(request)

        try:
            total_course = getattr(models,COURSEDETAILS_TABLE).objects.all().count()
            total_user = getattr(models,USERSIGNUP_TABLE).objects.filter(**{USER_TYPE:1}).count()
            supplier_course_count = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email}).count()

            purchased_course = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email}).count()

            Courses_Offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email}).order_by("-created_date_time")

        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in count details"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Individuals11 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email}).values_list("payment_detail__course_name",'user_profile__first_name','user_profile__email_id')
          
            user_name = [x[1] for x in Individuals11]
            user_email = [x[2] for x in Individuals11]
            course_name = [x[0] for x in Individuals11]
            individual_details = {}
            final_dict = {}
            individual_details [USERNAME] = user_name
            individual_details [COURSENAME] = course_name
            individual_details[USER_EMAIL] = user_email
            counter = 0
            for v in individual_details[COURSENAME]:
                Individuals = getattr(models,COURSEDETAILS_TABLE).objects.get(**{COURSE_NAME:v})
                final_dict[counter] = {
                    USERNAME:individual_details[USERNAME][counter],
                    USER_EMAIL:individual_details[USER_EMAIL][counter],
                    COURSE_ID:str(Individuals.uuid),
                    COURSENAME:v,
                    COURSETYPE:Individuals.course_type.type_name,
                }
                counter +=1
            print(final_dict)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Individual Course list Error"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            all_subcategory = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1})
        except Exception as ex:
            all_subcategory = None
        try:
            if all_subcategory_serializer := SubCategoryDetailsSerializer(all_subcategory, many=True):
                newvar = all_subcategory_serializer.data
        except Exception as ex:
            newvar = None
        if course_offer_serializer := CourseDetailsSerializer(Courses_Offered, many=True):
            return Response({STATUS: SUCCESS,
            TOTAL_COURSE_COUNT: total_course,
            TOTAL_USER_COUNT: total_user,
            SUPPLIER_COURSE_COUNT: supplier_course_count,
            PURCHASED_COURSE_COUNT: purchased_course,
            COURSE_OFFERED: course_offer_serializer.data,
            INDIVIDUALS: final_dict,
            ALL_SUBCATEGORY: newvar}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Error in Coursedetail user data"}, status=status.HTTP_400_BAD_REQUEST)
       

class SupplierDashboard_Active_InActiveView(APIView):
    def put(self,request):
        status_s = request.POST.get(STATUS)
        course_name = request.POST.get(COURSE_NAME)
        try:
            data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{COURSE_NAME:course_name})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {}
        record_map = {STATUS_ID: 1,} if status_s == "Active" else {STATUS_ID: 2,}

        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data Succesfully Edited"}, status=status.HTTP_200_OK)



class SupplierDashboard_courseGraphView(APIView):
    def post(self, request):
        supplier_email = get_user_email_by_token(request)
        time_period = request.POST.get(TIME_PERIOD)
        date = datetime.datetime.now()

        if time_period == WEEKLY:
            week = date.strftime("%V")
            try:
                course_offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__week":week}).count()
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "course offered error"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                purchased = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,'payment_detail__status':'Success',"created_date_time__week":week,}).values_list("payment_detail__course_name", flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "purchased course error"}, status=status.HTTP_400_BAD_REQUEST)
            set1 = set(purchased)
            purchased_course = len(set1)
            try:
                all_supplier_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__week":week}).values_list(COURSE_NAME, flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "all supplier course error"}, status=status.HTTP_400_BAD_REQUEST)

            set_all = set(all_supplier_course)
            non_purchased = len(set_all-set1)


        elif time_period == MONTHLY:
            month = date.strftime("%m")
            try:
                course_offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__month":month}).count()
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "course offered error"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                purchased = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__month":month,'payment_detail__status':'Success'}).values_list("payment_detail__course_name", flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "purchased course error"}, status=status.HTTP_400_BAD_REQUEST)
            set1 = set(purchased)
            purchased_course = len(set1)
            try:
                all_supplier_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__month":month}).values_list(COURSE_NAME, flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "all supplier course error"}, status=status.HTTP_400_BAD_REQUEST)
            set_all = set(all_supplier_course)
            non_purchased = len(set_all-set1)

        elif time_period == YEARLY:
            year = date.strftime("%Y")
            try:
                course_offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__year":year}).count()
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "course offered error"}, status=status.HTTP_400_BAD_REQUEST)
            try:

                purchased = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__year":year,'payment_detail__status':'Success'}).values_list("payment_detail__course_name", flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "purchased course error"}, status=status.HTTP_400_BAD_REQUEST)
            set1 = set(purchased)
            purchased_course = len(set1)
            try:
                all_supplier_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__year":year}).values_list(COURSE_NAME, flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "all supplier course error"}, status=status.HTTP_400_BAD_REQUEST)
            set_all = set(all_supplier_course)
            non_purchased = len(set_all-set1)

        return Response({STATUS: SUCCESS,
                COURSE_OFFERED: course_offered,
                PURCHASED:purchased_course,
                NOT_PURCHASED:non_purchased}, status=status.HTTP_200_OK)


class SupplierDashboard_earningGraphView(APIView):
    def post(self, request):
        supplier_email = get_user_email_by_token(request)
        time_period = request.POST.get(TIME_PERIOD)
        datee = datetime.datetime.now()

        if time_period == WEEKLY:
            week = datee.strftime("%V")
            today = datetime.datetime.now()
            week_list = {}
            try:
                for i in range(0, 7):
                    past = today - timedelta(days = i)
                    data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__date":past}).values_list("payment_detail__amount", flat=True)
                    var = list(data)
                    final = float(sum(var))
                    if var == "":
                        final = 0.0
                    week_list[past.strftime("%A")] = final
                data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__week":week}).values_list("payment_detail__amount", flat=True)
                total_earning = float(sum(list(data)))
                return Response({STATUS: SUCCESS,"total_earning": total_earning, DATA:week_list}, status=status.HTTP_200_OK)
            except Exception as ex: 
                return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)

        elif time_period == MONTHLY:
            month_list = {}
            month = datee.strftime("%m")
            first = datetime.datetime.today() - timedelta(days=30)
            second = first + timedelta(days=10)
            third = second + timedelta(days=10)
            try:
                data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__month":month}).values_list("payment_detail__amount", flat=True)

                data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__date__range":(first, second)}).values_list("payment_detail__amount", flat=True)
                month_list[str(first.date()) + " to " + str(second.date())] = float(sum(list(data1)))

                data2 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__date__range":(second, third)}).values_list("payment_detail__amount", flat=True)
                month_list[str(second.date())+ " to " +str(third.date())] = float(sum(list(data2)))

                data3 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__date__range":(third, datetime.datetime.today())}).values_list("payment_detail__amount", flat=True)
                month_list[str(third.date())+" to "+str(datetime.date.today())] = float(sum(list(data3)))

                total_earning = float(sum(list(data)))
                return Response({STATUS: SUCCESS,"total_earning": total_earning, DATA:month_list}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif time_period == YEARLY:
            month = datee.strftime("%m")
            try:
                today = datetime.datetime.now()
                # Get next month and year using relativedelta
                next_month = today + relativedelta(months=+1)
                # How many months do you want to go back?
                num_months_back = 12
                i = 0
                deque_months = deque()
                while i < num_months_back:
                    curr_date = today + relativedelta(months=-i)
                    deque_months.appendleft(curr_date.strftime('%B %Y'))

                    if i == num_months_back:
                        deque_months.append(next_month.strftime('%B %Y'))

                    i = i+1
                # Convert deque to list
                month_List = list(deque_months)
                year = datee.strftime("%Y")
                data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__year":year}).values_list("payment_detail__amount", flat=True)
                total_earning = float(sum(list(data)))
                final_data = {}
                for i in range(0, 12):
                    data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__year":month_List[i].split()[1], "created_date_time__month":strptime(month_List[i].split()[0],'%B').tm_mon}).values_list("payment_detail__amount", flat=True)
                    final_data[month_List[i].split()[0]] = float(sum(list(data1)))
                return Response({STATUS: SUCCESS,
                "total_earning": total_earning, DATA:final_data}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({STATUS: "Invalid time_period added", DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)




class CourseMaterialUpload(APIView):
    def post(self, request):
        email_id = get_user_email_by_token(request)   
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Method Not Allowed"}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     course_id = getattr(models,COURSEDETAILS_TABLE).objects.only(ID).get(**{COURSE_NAME:request.POST.get(COURSE_NAME,None)})
        #     print(course_id,'*****************************************************')
        # except Exception as ex:
        #     print(ex,"exxxxxxxxxxxxxxxx")
        #     return Response({STATUS:ERROR, DATA: "Error Getting Data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
        
            record_map = {
                # COURSE : course_id.id,
                VIDEO_TITLE : request.POST.get(VIDEO_TITLE,None),
                VIDEO_FILES : request.FILES.getlist(VIDEO_FILES,None),
                FILE_TITLE : request.POST.get(FILE_TITLE,None),
                DOCUMENT_FILES : request.FILES.getlist(DOCUMENT_FILES,None),
                } 
            record_map[CREATED_AT] = make_aware(datetime.datetime.now()) 
            for i in record_map.document_files:
                record_1 = {}
                record_1['document_file'] = i
                doc = getattr(models,"MaterialDocumentMaterial").objects.update_or_create(**record_1)
                
                doc.save()
            for j in record_map.video_files:
                file = getattr(models,"MaterialVideoMaterial").objects.update_or_create(**j)
                file.save()
            # getattr(models,"CourseMaterial").objects.update_or_create(**record_map)

            return Response({STATUS: SUCCESS, DATA: "Course Created successfully"}, status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex, "exxxxx")
            return Response({STATUS:ERROR, DATA: "Error Saving in record map"}, status=status.HTTP_400_BAD_REQUEST)

       

class SupplierOrganizationProfileview(APIView):
    def post(self, request):
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Method Not Allowed"}, status=status.HTTP_400_BAD_REQUEST)

        email_id = get_user_email_by_token(request)
        try:
            record_map = {
                SUPPLIER_EMAIL : request.POST.get(SUPPLIER_EMAIL,None),
                ORGANIZATIONAL_NAME : request.POST.get(ORGANIZATIONAL_NAME,None),
                ORGANIZATION_EMAIL : request.POST.get(ORGANIZATION_EMAIL,None),
                ORGANIZATION_WEBSITE : request.POST.get(ORGANIZATION_WEBSITE,None),
                ORGANIZATION_ADDRESS : request.POST.get(ORGANIZATION_ADDRESS,None),
                COUNTRY : request.POST.get(COUNTRY,None),
                CITY : request.POST.get(CITY,None),
                BRIF_INFORMATION : request.POST.get(BRIF_INFORMATION,None),
                ORGANIZATION_PHONE_NUMBER : request.POST.get(ORGANIZATION_PHONE_NUMBER,None),
                CONTECT_PERSON : request.POST.get(CONTECT_PERSON,None),
                COURSE_CATEGORY : request.POST.get(COURSE_CATEGORY,None),
                SUB_CATEGORY : request.POST.get(SUB_CATEGORY,None),
                ORGANIZATION_LOGO : request.FILES.get(ORGANIZATION_LOGO,None),
            }
            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            try:
                getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.update_or_create(**record_map)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Profile Created successfully"}, status=status.HTTP_200_OK)


    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except Exception as ex:
            data= None
        if serializer := SupplierOrganizationProfileSerializer(data):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self, request):
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Method Not Allowed"}, status=status.HTTP_400_BAD_REQUEST)

        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Not Able to get organization profile data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            record_map = {
                ORGANIZATIONAL_NAME : request.POST.get(ORGANIZATIONAL_NAME,data.organizational_name),
                ORGANIZATION_EMAIL : request.POST.get(ORGANIZATION_EMAIL,data.organization_email),
                ORGANIZATION_WEBSITE : request.POST.get(ORGANIZATION_WEBSITE,data.organization_website),
                ORGANIZATION_ADDRESS : request.POST.get(ORGANIZATION_ADDRESS,data.organization_address),
                COUNTRY : request.POST.get(COUNTRY,data.country),
                CITY : request.POST.get(CITY,data.city),
                BRIF_INFORMATION : request.POST.get(BRIF_INFORMATION,data.brif_information),
                ORGANIZATION_PHONE_NUMBER : request.POST.get(ORGANIZATION_PHONE_NUMBER,data.organization_phone_number),
                CONTECT_PERSON : request.POST.get(CONTECT_PERSON,data.contact_person),
                COURSE_CATEGORY : request.POST.get(COURSE_CATEGORY,data.course_category),
                SUB_CATEGORY : request.POST.get(SUB_CATEGORY,data.sub_category),
                ORGANIZATION_LOGO : request.FILES.get(ORGANIZATION_LOGO,data.organization_logo),
            }

            record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()            
            return Response({STATUS: SUCCESS, DATA: "Organization Profile Data edited successfully"}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in saving Edited data"}, status=status.HTTP_400_BAD_REQUEST)


class SupplierProfileView(APIView):
    def put(self, request):
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Method Not Allowed"}, status=status.HTTP_400_BAD_REQUEST)

        email_id = get_user_email_by_token(request)
        
        try:
            data = getattr(models,SUPPLIER_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except Exception as ex:
            data= None
        try:
            record_map = {
                SUPPLIER_NAME : request.POST.get(SUPPLIER_NAME,data.supplier_name),
                ADDRESS : request.POST.get(ADDRESS,data.address),
                PHONE_NUMBER : request.POST.get(PHONE_NUMBER,data.phone_number),
                SUPPLIER_IMAGE : request.FILES.get(SUPPLIER_IMAGE,data.supplier_image),
            }

            record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()            
            return Response({STATUS: SUCCESS, DATA: "Profile Data edited successfully"}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in saving Edited data"}, status=status.HTTP_400_BAD_REQUEST)

    
    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,SUPPLIER_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except Exception as ex:
            data= None
        if serializer := SupplierProfileSerializer(data):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)