from calendar import TUESDAY
from math import ceil
from posixpath import split
# from select import select
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
from moviepy.editor import VideoFileClip
from itertools import chain


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
            "meeting_link" : request.POST.get("meeting_link",None),
            "meeting_passcode" : request.POST.get("meeting_passcode",None),
            "target_users" : request.POST.get("target_users",None),
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
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)
        email_id = get_user_email_by_token(request)
        try:    
            supplier_id = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "error Getting Suppier Details"}, status=status.HTTP_400_BAD_REQUEST)
        user_type = supplier_id.user_type.user_type
        try:    
            category_id = getattr(models,COURSE_CATEGORY_TABLE).objects.get(**{CATEGORY_NAME:request.POST.get(CATEGORY_NAME_ID,None)})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "error Getting Category Name"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            SUPPLIER_ID: supplier_id.id,
            CATEGORY_NAME_ID: category_id.id,
            SUBCATEGORY_NAME: request.POST.get(SUBCATEGORY_NAME,None),
            SUBCATEGORY_IMAGE : request.FILES.get(SUBCATEGORY_IMAGE,None),
            IS_APPROVED_ID : 2,
            STATUS_ID:1
        }
        record_map[CREATED_AT] = make_aware(datetime.datetime.now())
        record_map[CREATED_BY] = user_type
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
            data = getattr(models,COURSE_CATEGORY_TABLE).objects.all().order_by("-created_date_time")
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
                elif user_type_data == SUPPLIER_S:
                    data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.filter(**{'supplier__email_id':email_id}).order_by("-created_date_time")
                else:
                    data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False}).order_by("-created_date_time")
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
        email_id =  get_user_email_by_token(request)
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
            STATUS_ID:2,
            IS_DELETED:True

        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = email_id
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
        try:
            vat = getattr(models,"InvoiceVATCMS").objects.all().values_list("vat_value", flat=True)
            vat_val = int(vat[0])
        except Exception as ex:
            vat_val = None
        if uuid:
            email_id = get_user_email_by_token(request)
            try:
                user = getattr(models,USER_PROFILE).objects.get(**{"email_id":email_id})
            except:
                user = None
            try:
                course_data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid})
            except:
                course_data = None
            try:
                supplier_profile = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{"supplier_email":course_data.supplier.email_id})
            except Exception as ex:
                supplier_profile = None
            try:
                fav_data = getattr(models,FAVOURITE_COURSE_TABLE).objects.filter(**{COURSE_NAME:course_data.course_name}).get(**{EMAIL_ID:email_id})
                fav_dataa = fav_data.is_favourite
            except Exception as ex:
                fav_data = None
                fav_dataa = None

            try:
                user_data = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{COURSE_NAME:course_data.course_name, STATUS:"Success"}).values_list("email_id", flat=True)
                individuals = getattr(models,USER_PROFILE_TABLE).objects.filter(**{"email_id__in":user_data, IS_DELETED:False})
                lerner_count = len(individuals)
            except Exception as e:
                individuals = None
                lerner_count = None
            try:
                var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, COURSE_NAME:course_data.course_name, STATUS:"Success"})
            except Exception as ex:
                var = None
            var1 = True if var is not None else False

            try:
                rating = getattr(models,"CourseRating").objects.filter(**{COURSE_NAME:course_data})
                l = []
                for i in rating:
                    l.append(int(i.star))
                final_rating = "{:.1f}".format(sum(l)/len(l))
            except Exception as ex:
                rating = None
                final_rating = None
            

            if serializer := CourseDetailsSerializer(course_data):
                if serializer1 := UserProfileSerializer(individuals, many=True):
                    if serializer2 := SupplierOrganizationProfileSerializer(supplier_profile):
                        if serializer3 := CourseRatingSerializer(rating, many=True):
                            return Response({STATUS: SUCCESS, DATA:serializer.data, "Supplier_Organization_Profile":serializer2.data, ENROLLED:serializer1.data, 'is_favoutite':fav_dataa, "learners_count":lerner_count, "is_enrolled": var1, "VAT_charges":vat_val, "rating":serializer3.data, "final_rating":final_rating}, status=status.HTTP_200_OK)
                        else:
                            return Response({STATUS: ERROR, DATA: serializer3.errors}, status=status.HTTP_400_BAD_REQUEST)
                    else: 
                         return Response({STATUS: ERROR, DATA: serializer2.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({STATUS: ERROR, DATA: serializer1.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
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

                    # organization_domain = email_id.split('@')[1]
                    course_enrolled = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{EMAIL_ID:email_id,STATUS:'Success'}).values_list("course_name", flat=True)
                    target_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False, "course_for_organization" : True, "target_users__icontains" : email_id}).exclude(course_name__in = course_enrolled)
                    target_course_data = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False,"course_for_organization" : True, "target_users__icontains" : email_id}).exclude(course_name__in = course_enrolled).values_list("course_name")
                    
                    
                    # data_category = getattr(models,COURSEDETAILS_TABLE).objects.filter(Q(organization_domain = organization_domain) | Q(course_category__category_name__in = a)).filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False}).exclude(course_name__in = course_enrolled).order_by("-organization_domain")

                    # data_category_list = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False}).filter(Q(organization_domain = organization_domain) | Q(course_category__category_name__in = a) | Q(course_name__in = course_enrolled)).values_list(COURSE_NAME, flat=True)

                    data_all = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False, "course_for_organization" : False,}).exclude(course_name__in = target_course_data and course_enrolled).order_by("-created_date_time")
                    print(data_all, "allllllllllll")
                    # final_queryset = list(chain(target_course, data_all))
                if serializer := CourseDetailsSerializer(target_course,many=True):
                    if serializer_all := CourseDetailsSerializer(data_all, many=True):
                        # return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
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
            enrolled = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{COURSE_NAME:data.course_name})
            if enrolled.exists():
                return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Course You Can't Edit"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            pass
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
            "meeting_link" : request.POST.get("meeting_link",data.meeting_link),
            "meeting_passcode" : request.POST.get("meeting_passcode",data.meeting_passcode),
            "target_users" : request.POST.get("target_users",data.target_users),
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
                                    path = 'eddi_app'
                                    img_dir = 'static'
                                    image = 'Logo.jpg'
                                    file_path = os.path.join(path,img_dir,image)
                                    with open(file_path,'rb') as f:
                                        img = MIMEImage(f.read())
                                        img.add_header('Content-ID', '<{name}>'.format(name=image))
                                        img.add_header('Content-Disposition', 'inline', filename=image)
                                    email_msg.attach(img)
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
                            path = 'eddi_app'
                            img_dir = 'static'
                            image = 'Logo.jpg'
                            file_path = os.path.join(path,img_dir,image)
                            with open(file_path,'rb') as f:
                                img = MIMEImage(f.read())
                                img.add_header('Content-ID', '<{name}>'.format(name=image))
                                img.add_header('Content-Disposition', 'inline', filename=image)
                            email_msg.attach(img)
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
                # record_map[UUID] = uuid4()
                print(record_map, "recordddddddddd")
                for key,value in record_map.items():
                    setattr(data,key,value)
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Data Succesfully Edited"}, status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex, "exxxxxxxxxxxxxxx")
            return Response({STATUS: ERROR, DATA: "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request,uuid = None):
        email_id =  get_user_email_by_token(request)
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
            STATUS_ID:2,
            IS_DELETED:True
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = email_id
        # record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data Succesfully Deleted"}, status=status.HTTP_200_OK)
    
class AdminDashboardView(APIView):
    def get(self, request,uuid = None): 
        admin_email = get_user_email_by_token(request)
        try:
            admin_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:admin_email})
            total_supplier = getattr(models,USERSIGNUP_TABLE).objects.filter(**{USER_TYPE_ID:1}).count()
            total_user = getattr(models,USERSIGNUP_TABLE).objects.filter(**{USER_TYPE_ID:2}).count()
            total_course = getattr(models,COURSEDETAILS_TABLE).objects.all().count()
            purchased_course = getattr(models,COURSE_ENROLL_TABLE).objects.all().count()
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in count details"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            users = getattr(models,USERSIGNUP_TABLE).objects.all().exclude(user_type_id = 3)
            course_supplier = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__user_type_id":1})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in getting tables data"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer :=  UserSignupSerializer(users, many = True):
            if serializer1 := CourseDetailsSerializer ( course_supplier, many = True):
                return Response({STATUS: SUCCESS,
            "admin_name" : admin_data.first_name + " " + admin_data.last_name,
            "supplier_count": total_supplier,
            "user_count": total_user,
            "total_course": total_course,
            PURCHASED_COURSE_COUNT: purchased_course,
            "users": serializer.data,
            "suppliers": serializer1.data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Error in Coursedetail user data"}, status=status.HTTP_400_BAD_REQUEST)



class SupplierDashboardView(APIView):
    def post(self, request,uuid = None):
        supplier_email = get_user_email_by_token(request)

        try:
            supplier_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{"email_id":supplier_email})
            total_course = getattr(models,COURSEDETAILS_TABLE).objects.all().count()
            total_user = getattr(models,USERSIGNUP_TABLE).objects.filter(**{USER_TYPE:1}).count()
            supplier_course_count = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email}).count()
            purchased_course = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email}).count()
            Courses_Offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email}).order_by("-created_date_time")

        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in count details"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Individuals11 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email}).values_list("payment_detail__course_name",'user_profile__first_name','user_profile__email_id')
            
            course_name = [x[0] for x in Individuals11]
            user_name = [x[1] for x in Individuals11]
            user_email = [x[2] for x in Individuals11]
            individual_details = {}
            final_dict = {}
            individual_details[USERNAME] = user_name
            individual_details[COURSENAME] = course_name
            individual_details[USER_EMAIL] = user_email
            counter = 0
            # print(individual_details, "indididididididi")
            for v in individual_details[COURSENAME]:
                print(v,"vvvvvvvvv")
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
            print(ex,"exexexexe")
            return Response({STATUS: ERROR, DATA: "Individual Course list Error"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            all_subcategory = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False})
        except Exception as ex:
            all_subcategory = None
        try:
            if all_subcategory_serializer := SubCategoryDetailsSerializer(all_subcategory, many=True):
                newvar = all_subcategory_serializer.data
        except Exception as ex:
            newvar = None
        if course_offer_serializer := CourseDetailsSerializer(Courses_Offered, many=True):
            return Response({STATUS: SUCCESS,
            "supplier_name" :supplier_data.first_name + " " + supplier_data.last_name,
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
                    # final = float(sum(var))
                    final = "{:.2f}".format(sum(var))
                    if var == "":
                        final = 0.0
                    week_list[past.strftime("%A")] = final
                data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__week":week}).values_list("payment_detail__amount", flat=True)
                # total_earning = float(sum(list(data)))
                total_earning = "{:.2f}".format(sum(list(data)))
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
                month_list[str(first.date()) + " to " + str(second.date())] = "{:.2f}".format(sum(list(data1)))

                data2 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__date__range":(second, third)}).values_list("payment_detail__amount", flat=True)
                month_list[str(second.date())+ " to " +str(third.date())] = "{:.2f}".format(sum(list(data2)))

                data3 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__date__range":(third, datetime.datetime.today())}).values_list("payment_detail__amount", flat=True)
                month_list[str(third.date())+" to "+str(datetime.date.today())] = "{:.2f}".format(sum(list(data3)))

                # total_earning = float(sum(list(data)))
                total_earning = "{:.2f}".format(sum(list(data)))
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
                total_earning = "{:.2f}".format(sum(list(data)))
                final_data = {}
                for i in range(0, 12):
                    data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__year":month_List[i].split()[1], "created_date_time__month":strptime(month_List[i].split()[0],'%B').tm_mon}).values_list("payment_detail__amount", flat=True)
                    final_data[month_List[i].split()[0]] = "{:.2f}".format(sum(list(data1)))
                return Response({STATUS: SUCCESS,
                "total_earning": total_earning, DATA:final_data}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({STATUS: "Invalid time_period added", DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)




class CourseMaterialUpload(APIView):
    def post(self, request, uuid=None):
        print("inside posttttttttttttttttttttttt")
        email_id = get_user_email_by_token(request)   
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Method Not Allowed"}, status=status.HTTP_400_BAD_REQUEST)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "uuid not given"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            video_title = request.POST.get(VIDEO_TITLE,None)
            video_files = request.FILES.getlist(VIDEO_FILES,None)
            file_title = request.POST.get(FILE_TITLE,None)
            document_files = request.FILES.getlist(DOCUMENT_FILES,None)
            course_data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid})
            print(video_files, "videooooooooo")
            print(document_files, "documenttttt")
            print(request.FILES, "filesssssss")
            reccord_map = {}
            reccord_map = {
                "video_title" : video_title,      
                "file_title"  : file_title,
                "course_id" : course_data.id
                }
            print(reccord_map, "recordddddd")
            data = getattr(models,"CourseMaterial").objects.update_or_create(**reccord_map)
            print("saveddddddddddddddddddddddd")
            if request.FILES.getlist(DOCUMENT_FILES):
                try:
                    for i in document_files:
                        # clip = VideoFileClip(str(i))
                        # print(clip.duration, "durararararararararar")
                        print(i, "iiiii")
                        data1 = getattr(models,"MaterialDocumentMaterial").objects.update_or_create(**{"document_file":i})
                        print(data1, "data11111")
                        data[0].document_files.add(data1[0].id)
                except Exception as ex:
                    print(ex, "exexexexe")
                    return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)
            if request.FILES.getlist("video_files"):
                try:
                    for j in video_files:
                        data2 = getattr(models,"MaterialVideoMaterial").objects.update_or_create(**{"video_file":j})
                        print(data2, "data2222")

                        data[0].video_files.add(data2[0].id)
                except Exception as ex:
                    print(ex, "exexexexe")
                    return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)      
        return Response({STATUS: SUCCESS, DATA: "Material Uploaded successfully"}, status=status.HTTP_200_OK)
    
    def get(self, request, uuid=None):
        email_id = get_user_email_by_token(request) 
        print("uuid",uuid)
        response_dict = {}
        if uuid:
            try:
                course_material_data = getattr(models,"CourseMaterial").objects.get(**{"course__uuid":uuid})
                print("course Data",course_material_data)
            except Exception as ex:
                print(ex,"exexexe")
                course_material_data = None
            # try:
            #     course_material_status = getattr(models,"CourseMaterialStatus").objects.filter(**{'user_email':email_id})
            #     for i in course_material_status:
            #         print(i.is_complete)
            # except Exception as ex:
            #     course_material_status = None
            if serializer := CourseMaterialSerializer(course_material_data):
                print(serializer.data, "datatatat")
                # if serializer1 := CourseMaterialStatusSerializer(course_material_status, many=True):
                    # return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: ERROR, DATA: "uuid not provided"}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, uuid=None):
        email_id = get_user_email_by_token(request)   
        if not uuid:
            return Response({STATUS: ERROR, DATA: "uuid not given"}, status=status.HTTP_400_BAD_REQUEST)
        print("inside puttt")
        course_material_data = getattr(models,"CourseMaterial").objects.get(**{"course__uuid":uuid})
        video_title = request.POST.get(VIDEO_TITLE,course_material_data.video_title)
        video_files = request.FILES.getlist(VIDEO_FILES,None)
        video_files_old = request.POST.getlist("video_files_old",None)
        file_title = request.POST.get(FILE_TITLE,course_material_data.file_title)
        document_files = request.FILES.getlist(DOCUMENT_FILES,None)
        document_files_old = request.POST.getlist("document_files_old",None)
        # course_data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid})
        # print(document_files_old, "oldddddocu")
        reccord_map = {}
        reccord_map = {
            "video_title" : video_title,      
            "file_title"  : file_title,
            # "course_id" : course_data.id
            }
        for key, value in reccord_map.items():
            setattr(course_material_data, key, value)
        course_material_data.save()
        # print("PUTTTTTTTTTTTTT")
        print(request.FILES.getlist(DOCUMENT_FILES), "filesssssss")
        # print("inside doccccc")
        try:
            old_docs = course_material_data.document_files.all()
            # print(old_docs, "docssss")
            new = list(old_docs)
            oldd = [i.document_file.url for i in new]
            # print(oldd,"OOOOOOOOOOOOOOOOOOOOOOO")
            # print(new, "newewewewe")
            for i in document_files_old:
                if i in oldd:
                    # print("OKOK") 
                    oldd.remove(i)
            # print(oldd,"oldddd")
            # print(document_files_old)
                    
            for k in oldd:
                try:
                    getattr(models,"MaterialDocumentMaterial").objects.get(**{"document_file":k[7:]}).delete()
                    print("deleted")
                except Exception as ex:
                    print(ex, "exexexexe")
            if document_files:
                for i in document_files:
                    print("inside iiiii")
                    data1 = getattr(models,"MaterialDocumentMaterial").objects.update_or_create(**{"document_file":i})
                    print(data1, "data11111")
                    course_material_data.document_files.add(data1[0].id)
               
        except Exception as ex:
            print(ex, "exexexexe")
            return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            old_videos = course_material_data.video_files.all()
            new1 = list(old_videos)
            oldd1 = [i.video_file.url for i in new1]
            # print(oldd1,"OOOOOOOOOOOOOOOOOOOOOOO")
            # print(new1, "newewewewe")
            for i in video_files_old:
                if i in oldd1:
                    # print("OKOK") 
                    oldd1.remove(i)
            # print(oldd1,"oldddd")
            print(video_files_old)
            for j in oldd1:
                try:
                    getattr(models,"MaterialVideoMaterial").objects.get(**{"video_file":j[7:]}).delete()
                    print("deleted")
                except Exception as ex:
                    print(ex,"exexexexe")
        
            for p in video_files:
                # print("inside pppp")
                data3 = getattr(models,"MaterialVideoMaterial").objects.update_or_create(**{"video_file":p})
                # print(data3, "data3333")
                course_material_data.video_files.add(data3[0].id)
                
        except Exception as ex:
            print(ex, "exexexexe")
            return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)      
        return Response({STATUS: SUCCESS, DATA: "Material Edited successfully"}, status=status.HTTP_200_OK)

       

class SupplierOrganizationProfileview(APIView):
    def post(self, request):
        email_id = get_user_email_by_token(request)
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Method Not Allowed"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            record_map = {
                SUPPLIER_EMAIL : email_id,
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
                print("savedddd")
            except Exception as ex:
                print(ex,"exexeex")
                return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Profile Created successfully"}, status=status.HTTP_200_OK)


    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except Exception as ex:
            print(ex,"exxexe")
            data= None
        if serializer := SupplierOrganizationProfileSerializer(data):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self, request):
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
        email_id = get_user_email_by_token(request)

        try:
            data = getattr(models,SUPPLIER_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except Exception as ex:
            print(ex, "exexexe")
            data= None
        if data is not None:
            try:
                record_map = {
                    SUPPLIER_NAME : request.POST.get(SUPPLIER_NAME,data.supplier_name),
                    SUPPLIER_EMAIL : email_id,
                    ADDRESS : request.POST.get(ADDRESS,data.address),
                    PHONE_NUMBER : request.POST.get(PHONE_NUMBER,data.phone_number),
                    SUPPLIER_IMAGE : request.FILES.get(SUPPLIER_IMAGE,data.supplier_image),
                    ABOUT_ME : request.POST.get(ABOUT_ME,data.about_me),
                }

                record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
                for key,value in record_map.items():
                    setattr(data,key,value)
                data.save()            
                return Response({STATUS: SUCCESS, DATA: "Profile Data edited successfully"}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error in saving Edited data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                record_map = {
                    SUPPLIER_NAME : request.POST.get(SUPPLIER_NAME,None),
                    SUPPLIER_EMAIL : email_id,
                    ADDRESS : request.POST.get(ADDRESS,None),
                    PHONE_NUMBER : request.POST.get(PHONE_NUMBER,None),
                    SUPPLIER_IMAGE : request.FILES.get(SUPPLIER_IMAGE,None),
                    ABOUT_ME : request.POST.get(ABOUT_ME, None),
                }
                record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
                getattr(models,SUPPLIER_PROFILE_TABLE).objects.update_or_create(**record_map)
                return Response({STATUS: SUCCESS, DATA: "Profile Data created successfully"}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error in saving Edited data"}, status=status.HTTP_400_BAD_REQUEST)


    
    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,SUPPLIER_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Requested Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer := SupplierProfileSerializer(data):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class MyProgressView(APIView):
    def get(self, request, uuid=None):
        email_id = get_user_email_by_token(request)
        time_period = request.POST.get(TIME_PERIOD)
        datee = datetime.datetime.now()

        if time_period == WEEKLY:
            week = datee.strftime("%V")
            today = datetime.datetime.now()
            week_list = {}


            try:
                enroll_data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{'user_profile__email_id':email_id}).values_list("payment_detail__course_name", flat = True)
            except Exception as ex:
                enroll_data = None
            try:
                course_data = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{'course_name__in':list(enroll_data)})
                print(course_data, "course_dataaa")
            except:
                course_data = None




            try:
                for i in range(0, 7):
                    past = today - timedelta(days = i)
                    data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__date":past}).values_list("payment_detail__amount", flat=True)
                    var = list(data)
                    # final = float(sum(var))
                    final = "{:.2f}".format(sum(var))
                    if var == "":
                        final = 0.0
                    week_list[past.strftime("%A")] = final
                data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__week":week}).values_list("payment_detail__amount", flat=True)
                # total_earning = float(sum(lis
                
                total_earning = "{:.2f}".format(sum(list(data)))
                return Response({STATUS: SUCCESS,"total_earning": total_earning, DATA:week_list}, status=status.HTTP_200_OK)
            except Exception as ex: 
                return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)
