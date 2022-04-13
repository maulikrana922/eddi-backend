from calendar import TUESDAY
from typing import final
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
        record_map = {
            SUPPLIER_ID: supplier_id.id,
            COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,None),
            COURSE_NAME: request.POST.get(COURSE_NAME,None),
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
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.filter(**{'supplier__email_id':email_id,STATUS_ID:1})
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
            print(dataa.id)
        except Exception as ex:
            print(ex)

            return Response({STATUS: ERROR, DATA: "Category Error"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {

            'category_name_id': dataa.id,
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
            STATUS_ID:2
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
                fav_data = getattr(models,FAVOURITE_COURSE_TABLE).objects.filter(**{'course_name':course_data.course_name}).get(**{EMAIL_ID:email_id})
                fav_dataa = fav_data.is_favourite
            except Exception as ex:
                fav_data = None
                fav_dataa = None

            try:
                individuals = models.CourseEnroll.objects.filter(payment_detail__course_name = course_data.course_name, payment_detail__status="Success")
              
            except Exception as e:
                print(e, "ererererer")
                individuals = None
            
            
            if serializer := CourseDetailsSerializer(course_data):
                if serializer1 := CourseEnrollSerializer(individuals, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data,"Enrolled": serializer1.data,'is_favoutite':fav_dataa}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors,"Enrolled": "No Enrolled User"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
            email_id =  get_user_email_by_token(request)
            if email_id:
                print(email_id)
              
                if getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == SUPPLIER_S:
                    data_s = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS:1,'supplier__email_id':email_id})
                    print("44444444444444")
                    for i in data_s:
                        print(i.course_name, "iiiiiiiiiiiiii")
                        total_individuals = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__course_name":i.course_name}).count()
                        print(total_individuals, "totallllllllllll")
                else:
                    cat = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                    print(cat, "cattttttttttttttt")
                    a = cat.course_category.split(",")
                    print(a, "listtttttt")
                    # print("555555555555555")
                    organization_domain = email_id.split('@')[1]
                    data_s = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS:1}).filter(Q(organization_domain = organization_domain) | Q(course_for_organization = False))
                    # data_s = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS:1}).filter(Q(organization_domain = organization_domain) | Q(course_for_organization = False)).extra(select={"cate_order":"course_category__category_name__in = a"})
                    print(data_s, "datassssss")
                    # data_s = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"course_category__category_name__in":a})
                    # print(data_s, "data_ssssssssssssssss")
           
                if serializer := CourseDetailsSerializer(data_s,many=True):
                    print("1111111111111111111111")
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                   
                #     print(i.organization_domain)
            else:
                data_s = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS:1}).exclude(**{'course_for_organization':True})
                
           
             
            # print(data)
            if serializer := CourseDetailsSerializer(data_s):
                print("222222222222222222222222")

                return Response({STATUS: SUCCESS, DATA: data_s}, status=status.HTTP_200_OK)

                # if serializer1 := CourseEnrollSerializer(individuals, many=True):
                #     return Response({STATUS: SUCCESS, DATA: serializer.data,"Enrolled": serializer1.data,'is_favoutite':fav_dataa}, status=status.HTTP_200_OK)
                # else:
                #     return Response({STATUS: SUCCESS, DATA: serializer.data,"Enrolled": "No Enrolled User",'is_favoutite':fav_dataa}, status=status.HTTP_200_OK)
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
        except Exception:
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

            purchased_course = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email}).count()

            Courses_Offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email})

        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in count details"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Individuals11 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email}).values_list("payment_detail__course_name",'user_profile__first_name','user_profile__email_id')
          
            user_name = [x[1] for x in Individuals11]
            user_email = [x[2] for x in Individuals11]
            course_name = [x[0] for x in Individuals11]
            individual_details = {}
            final_dict = {}
            individual_details ['username'] = user_name
            individual_details ['coursename'] = course_name
            individual_details['user_email'] = user_email
            counter = 0
            for v in individual_details['coursename']:
                Individuals = getattr(models,COURSEDETAILS_TABLE).objects.get(**{"course_name":v})
                final_dict[counter] = {
                    'username':individual_details['username'][counter],
                    'user_email':individual_details['user_email'][counter],
                    'course_id':str(Individuals.uuid),
                    'coursename':v,
                    'coursetype':Individuals.course_type.type_name,
                }
                counter +=1
            print(final_dict)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Individual Course list Error"}, status=status.HTTP_400_BAD_REQUEST)
        
        if course_offer_serializer := CourseDetailsSerializer(Courses_Offered, many=True):
            return Response({STATUS: SUCCESS,
            "total_course_count": total_course,
            "total_user_count":total_user,
            "supplier_course_count":supplier_course_count,
            "purchased_course_count":purchased_course,
            "Course_Offered":course_offer_serializer.data,
            "Individuals": final_dict}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Error in Coursedetail user data"}, status=status.HTTP_400_BAD_REQUEST)
       

class SupplierDashboard_Active_InActiveView(APIView):
    def put(self,request):
        status_s = request.POST.get("status")
        course_name = request.POST.get("course_name")
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
        time_period = request.POST.get("time_period")
        date = datetime.datetime.now()

        if time_period == "weekly":
            week = date.strftime("%V")
            try:
                course_offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__week":week}).count()
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "course offered error"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                purchased = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,'payment_detail__status':'Success',"created_date_time__week":week,}).values_list("payment_detail__course_name", flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "purchased course error"}, status=status.HTTP_400_BAD_REQUEST)
            set1 = set(purchased)
            purchased_course = len(set1)
            try:
                all_supplier_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__week":week}).values_list("course_name", flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "all supplier course error"}, status=status.HTTP_400_BAD_REQUEST)

            set_all = set(all_supplier_course)
            non_purchased = len(set_all-set1)


        elif time_period == "monthly":
            month = date.strftime("%m")
            try:
                course_offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__month":month}).count()
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "course offered error"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                purchased = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,"created_date_time__month":month,'payment_detail__status':'Success'}).values_list("payment_detail__course_name", flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "purchased course error"}, status=status.HTTP_400_BAD_REQUEST)
            set1 = set(purchased)
            purchased_course = len(set1)
            try:
                all_supplier_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__month":month}).values_list("course_name", flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "all supplier course error"}, status=status.HTTP_400_BAD_REQUEST)
            set_all = set(all_supplier_course)
            non_purchased = len(set_all-set1)

        elif time_period == "yearly":
            year = date.strftime("%Y")
            try:
                course_offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__year":year}).count()
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "course offered error"}, status=status.HTTP_400_BAD_REQUEST)
            try:

                purchased = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,"created_date_time__year":year,'payment_detail__status':'Success'}).values_list("payment_detail__course_name", flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "purchased course error"}, status=status.HTTP_400_BAD_REQUEST)
            set1 = set(purchased)
            purchased_course = len(set1)
            try:
                all_supplier_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__year":year}).values_list("course_name", flat=True)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "all supplier course error"}, status=status.HTTP_400_BAD_REQUEST)
            set_all = set(all_supplier_course)
            non_purchased = len(set_all-set1)

        return Response({STATUS: SUCCESS,
                "Course_Offered": course_offered,
                "Purchased":purchased_course,
                "Not_Purchased":non_purchased}, status=status.HTTP_200_OK)


class SupplierDashboard_earningGraphView(APIView):
    def post(self, request):
        supplier_email = get_user_email_by_token(request)
        time_period = request.POST.get("time_period")
        datee = datetime.datetime.now()

        if time_period == "weekly":
            week = datee.strftime("%V")
            today = datetime.datetime.now()
            week_list = {}
            try:
                for i in range(0, 7):
                    past = today - timedelta(days = i)
                    data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,"created_date_time__date":past}).values_list("payment_detail__amount", flat=True)
                    var = list(data)
                    final = float(sum(var))
                    if var == "":
                        final = 0.0
                    week_list[past.strftime("%A")] = final
                data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,"created_date_time__week":week}).values_list("payment_detail__amount", flat=True)
                total_earning = sum(list(data))
                return Response({STATUS: SUCCESS,"total_earning": total_earning, "weekly_earning":week_list}, status=status.HTTP_200_OK)
            except Exception as ex: 
                return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)

        elif time_period == "monthly":
            month_list = {}
            month = datee.strftime("%m")
            first = datetime.datetime.today() - timedelta(days=30)
            second = first + timedelta(days=10)
            third = second + timedelta(days=10)
            try:
                data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,"created_date_time__month":month}).values_list("payment_detail__amount", flat=True)

                data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,"created_date_time__date__range":(first, second)}).values_list("payment_detail__amount", flat=True)
                month_list[str(first.date()) + " to " + str(second.date())] = float(sum(list(data1)))

                data2 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,"created_date_time__date__range":(second, third)}).values_list("payment_detail__amount", flat=True)
                month_list[str(second.date())+ " to " +str(third.date())] = float(sum(list(data2)))

                data3 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,"created_date_time__date__range":(third, datetime.datetime.today())}).values_list("payment_detail__amount", flat=True)
                month_list[str(third.date())+" to "+str(datetime.date.today())] = float(sum(list(data3)))

                total_earning = int(sum(list(data)))
                return Response({STATUS: SUCCESS,
                "total_earning": total_earning, "monthly_earning":month_list}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif time_period == "yearly":
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
                data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,"created_date_time__year":year}).values_list("payment_detail__amount", flat=True)
                total_earning = int(sum(list(data)))
                final_data = {}
                for i in range(0, 12):
                    data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"supplier_email":supplier_email,"created_date_time__year":month_List[i].split()[1], "created_date_time__month":strptime(month_List[i].split()[0],'%B').tm_mon}).values_list("payment_detail__amount", flat=True)
                    final_data[month_List[i].split()[0]] = float(sum(list(data1)))
                return Response({STATUS: SUCCESS,
                "total_earning": total_earning, "final_list":final_data}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({STATUS: "Invalid time_period added", DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)




class CourseMaterialUpload(APIView):
    def post(self, request):
        video_title = request.POST.get(VIDEO_TITLE,None)
        video_files = request.POST.getlist(VIDEO_FILES,None)
        file_title = request.POST.get(FILE_TITLE,None)
        document_files = request.POST.getlist(DOCUMENT_FILES,None)

        try:
            course_id = getattr(models,COURSEDETAILS_TABLE).objects.only(ID).get(**{COURSE_NAME:request.POST.get(COURSE_NAME,None)})
        except Exception as ex:
            print(ex)

        