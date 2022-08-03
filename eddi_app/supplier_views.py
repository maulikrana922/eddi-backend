import json
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
# from moviepy.editor import *
import moviepy.editor
from itertools import chain
import cv2
# import pafy
from .notification import send_notification
from translate import Translator
from django.db import connection
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

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
    except:
        data = None
        return data

class AddCourseView(APIView):
    def post(self, request):
        res = None
        email_id = get_user_email_by_token(request)
        course_organization = None
        if request.POST.get(COURSE_NAME):
            try:
                course_data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{"course_name":request.POST.get(COURSE_NAME)})
            except:
                course_data = None
            if course_data != None:
                return Response({STATUS: ERROR, DATA: "Please choose unique course name", DATA_SV:"Vänligen, välj ett unikt namn på utbildningen"}, status=status.HTTP_400_BAD_REQUEST)
        if request.POST.get(COURSE_FOR_ORGANIZATION) == 'true':
            course_organization = True
            test_str = email_id
            res = test_str.split('@')[1]
        else:
            course_organization = False
        try:    
            supplier_id = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
        except Exception as ex:
            return Response({STATUS: ERROR,"var":str(ex), DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            category_id = getattr(models,COURSE_CATEGORY_TABLE).objects.only(ID).get(**{CATEGORY_NAME:request.POST.get(COURSE_CATEGORY_ID,None)})
            try:
                sub_category_id = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.only(ID).get(**{SUBCATEGORY_NAME:request.POST.get(SUBCATEGORY_NAME_ID,None)})
            except:
                sub_category_id = None
            course_type_id = getattr(models,COURSE_TYPE_TABLE).objects.only(ID).get(**{TYPE_NAME:request.POST.get(COURSE_TYPE_ID,None)})
            fee_type_id = getattr(models,FEE_TYPE_TABLE).objects.only(ID).get(**{FEE_TYPE_NAME :request.POST.get(FEE_TYPE_ID,None)})
            course_level_id = getattr(models,COURSE_LEVEL_TABLE).objects.only(ID).get(**{LEVEL_NAME : request.POST.get(COURSE_LEVEL_ID,None)})
            
        except Exception as ex:
            return Response({STATUS:ERROR,"var":str(ex), DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            organization_data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{"supplier_email":email_id})
        except:
            organization_data = None
        try:
            try:
                record_map = {
                SUPPLIER_ID: supplier_id.id,
                COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,None),
                COURSE_NAME: request.POST.get(COURSE_NAME,None),
                COURSE_LEVEL_ID : course_level_id.id,
                COURSE_LENGTH : request.POST.get(COURSE_LENGTH,None),
                COURSE_CATEGORY_ID :category_id.id ,
                COURSE_TYPE_ID : course_type_id.id,
                FEE_TYPE_ID: fee_type_id.id,
                COURSE_FOR_ORGANIZATION:course_organization,
                ORGANIZATION_DOMAIN:res,
                COURSE_LANGUAGE:request.POST.get(COURSE_LANGUAGE),
                COURSE_CHECKOUT_LINK: request.POST.get(COURSE_CHECKOUT_LINK,None),
                ADDITIONAL_INFORMATION: request.POST.get(ADDITIONAL_INFORMATION,None),
                ORGANIZATION_LOCATION: request.POST.get(ORGANIZATION_LOCATION,None),
                MEETING_LINK : request.POST.get(MEETING_LINK,None),
                MEETING_PASSCODE : request.POST.get(MEETING_PASSCODE,None),
                AUTHOR_NAME : request.POST.get(AUTHOR_NAME,None),
                AUTHOR_BIO : request.POST.get(AUTHOR_BIO,None),
                IS_POST : json.loads(request.POST.get(IS_POST)),
                TARGET_USERS : request.POST.get(TARGET_USERS,None),
                SUB_AREA:request.POST.get(SUB_AREA,None),
                IS_APPROVED_ID : 2,
                STATUS_ID:1,
                VAR_CHARGES : getattr(models,"InvoiceVATCMS").objects.latest(CREATED_AT)
                }
                if sub_category_id != None:
                    record_map[COURSE_SUBCATEGORY_ID] = sub_category_id.id
                if organization_data != None:
                    record_map["supplier_organization_id"] = organization_data.id
                if request.POST.get(COURSE_PRICE):
                    record_map[COURSE_PRICE] = "{:.2f}".format(float(request.POST.get(COURSE_PRICE)))
                try:
                    if request.POST.get("offer_price"):
                        record_map["offer_price"] = "{:.2f}".format(float(request.POST.get("offer_price")))
                except:
                    pass
                if request.POST.get(COURSE_STARTING_DATE) == "":
                    record_map[COURSE_STARTING_DATE] = None
                else:
                    record_map[COURSE_STARTING_DATE] = request.POST.get(COURSE_STARTING_DATE)
                record_map[CREATED_AT] = make_aware(datetime.datetime.now())
                record_map[CREATED_BY] = supplier_id.user_type
                print(record_map, "recordddd")
            except Exception as ex:
                return Response({STATUS:ERROR, "var":str(ex), DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
                
            getattr(models,COURSEDETAILS_TABLE).objects.update_or_create(**record_map)

            # noti to Admin
            if supplier_id.user_type.user_type != ADMIN_S:
                try:
                    message = f"{supplier_id.first_name}, has added a new course {request.POST.get(COURSE_NAME)}, under {category_id.category_name} to the system."
                    data = getattr(models,USERSIGNUP_TABLE).objects.filter(user_type__user_type = "Admin")
                    receiver = [i.email_id for i in data]
                    course = request.POST.get(COURSE_NAME)
                    try:
                        translator= Translator(from_lang='english',to_lang="swedish")
                        message_sv = translator.translate(f"{supplier_id.first_name}, has added a new course {course}, under {category_id.category_name} to the system.")
                    except:
                        pass
                    send_notification(email_id, receiver, message)
                    # receiver_device_token = []
                    # for i in data:
                    #     device_data = UserDeviceToken.objects.filter(user_type=i)
                    #     for j in device_data:
                    #         receiver_device_token.append(j.device_token)

                    # print(receiver_device_token)
                    # send_push_notification(receiver_device_token,message)
                    for i in receiver:
                        try:
                            record_map1 = {}
                            record_map1 = {
                                "sender" : email_id,
                                "receiver" : i,
                                "message" : message,
                                "message_sv" : message_sv,
                            }

                            getattr(models,"Notification").objects.update_or_create(**record_map1)
                        except:
                            pass
                except:
                    pass
            # noti to user
            try:
                users = getattr(models,USER_PROFILE_TABLE).objects.filter(**{"user_interests__icontains":category_id.category_name})
                print(users,"usersssss")
                if organization_data != None:
                    message = f"{supplier_id.first_name} from {organization_data.organizational_name}, has added a new Course under “{category_id.category_name}”"
                    message_sv = f"{supplier_id.first_name} från {organization_data.organizational_name}, har lagt till en utbildning inom kategorin/området “{category_id.category_name}”"
                else:
                    message = f"{supplier_id.first_name}, has added a new Course under “{category_id.category_name}”"
                    message_sv = f"{supplier_id.first_name}, har lagt till en utbildning inom kategorin/området “{category_id.category_name}”"
                receiver = [i.email_id for i in users]
                send_notification(email_id, receiver, message)
                # receiver_device_token = []
                # for i in users:
                #     device_data = UserDeviceToken.objects.filter(user_type=i.usersignup)
                #     for j in device_data:
                #         receiver_device_token.append(j.device_token)

                # print(receiver_device_token)
                # send_push_notification(receiver_device_token,message)
                for i in receiver:
                    try:
                        record_map2 = {}
                        record_map2 = {
                            "sender" : email_id,
                            "receiver" : i,
                            "message" : message,
                            "message_sv" : message_sv,
                        }

                        getattr(models,"Notification").objects.update_or_create(**record_map2)
                    except:
                        pass
            except:
                pass
            return Response({STATUS: SUCCESS, DATA: "Congratulations! Course created successfully", DATA_SV:"Grattis, er utbildning har nu lagts till!"}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS:ERROR, "var":str(ex), DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


class AddSubCategoryView(APIView):
    def post(self, request):
        email_id = get_user_email_by_token(request)
        try:    
            supplier_id = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        user_type = supplier_id.user_type.user_type
        try:    
            category_id = getattr(models,COURSE_CATEGORY_TABLE).objects.get(**{CATEGORY_NAME:request.POST.get(CATEGORY_NAME_ID,None)})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
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
        try:
            message = f"{supplier_id.first_name}, has added a new “{request.POST.get(SUBCATEGORY_NAME)}”, under “{category_id.category_name}”  to the system. Click below to view the details."
            data = getattr(models,USERSIGNUP_TABLE).objects.filter(user_type__user_type = "Admin")
            receiver = [i.email_id for i in data]
            subcategory = request.POST.get(SUBCATEGORY_NAME)
            try:
                translator= Translator(from_lang='english',to_lang="swedish")
                message_sv = translator.translate(f"{supplier_id.first_name}, has added a new “{subcategory}”, under “{category_id.category_name}”  to the system. Click below to view the details.")
            except:
                pass
            send_notification(email_id, receiver, message)
            # receiver_device_token = []
            # for i in data:
            #     device_data = UserDeviceToken.objects.filter(user_type=i)
            #     for j in device_data:
            #         receiver_device_token.append(j.device_token)

            # print(receiver_device_token)
            # send_push_notification(receiver_device_token,message)
            for i in receiver:
                try:
                    record_map1 = {}
                    record_map1 = {
                        "sender" : email_id,
                        "receiver" : i,
                        "message" : message,
                        "message_sv" : message_sv
                    }
                    getattr(models,"Notification").objects.update_or_create(**record_map1)
                except:
                    pass
        except:
            pass
        return Response({STATUS: SUCCESS, DATA: "Sub-category created successfully", DATA_SV:"Underkategori har nu skapats"}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class GetCategoryDetails(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,COURSE_CATEGORY_TABLE).objects.get(**{UUID:uuid, IS_DELETED:False})
            course_list = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"course_category_id":data.id})
            if serializer := CategoryDetailsSerializer(data):
                if serializer1 := CourseDetailsSerializer(course_list, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data, "course":serializer1.data}, status=status.HTTP_200_OK)
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
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.get(**{UUID:uuid, IS_DELETED:False})
            if serializer := SubCategoryDetailsSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            email_id = get_user_email_by_token(request)
            try:
                user_data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
            except Exception:
                user_data.user_type.user_type = None
            if user_data.user_type.user_type:
                if user_data.user_type.user_type == ADMIN_S:
                    data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.filter(**{IS_DELETED:False}).order_by("-created_date_time")
                elif user_data.user_type.user_type == SUPPLIER_S:
                    data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.filter(**{'supplier__email_id':email_id, IS_DELETED:False}).order_by("-created_date_time")
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
        except:
            user_type_data = None
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.get(**{UUID:uuid})
        except:
            return Response({STATUS: ERROR, DATA: "Requested data not found", DATA_SV:"Efterfrågad information kan inte hittas"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            dataa = getattr(models,COURSE_CATEGORY_TABLE).objects.get(**{CATEGORY_NAME:request.POST.get(CATEGORY_NAME_ID,data.category_name.category_name)})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {
            CATEGORY_NAME_ID: dataa.id,
            SUBCATEGORY_NAME: request.POST.get(SUBCATEGORY_NAME,data.subcategory_name),
            SUBCATEGORY_IMAGE : request.FILES.get(SUBCATEGORY_IMAGE,data.subcategory_image),
         }
        except:
            pass
        if user_type_data:
            if user_type_data == ADMIN_S:
                if request.POST.get(STATUS):
                    if request.POST.get(STATUS) == "Active":
                        record_map[STATUS_ID] = 1
                    else:
                        try:
                            data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{COURSE_CATEGORY:data.category_name})
                        except:
                            data1 = None
                        if data1.exists():
                            return Response({STATUS: ERROR, DATA: "Someone has already enrolled in this category", DATA_SV:"Någon har redan registrerat sig inom denna kategori, kategori kan inte raderas"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            record_map[STATUS_ID] = 2
                else:
                    record_map[STATUS] = data.status
                    
                if request.POST.get(APPROVAL_STATUS):
                    if request.POST.get(APPROVAL_STATUS) == "Approved":
                        record_map[IS_APPROVED_ID] = 1
                        try:
                            message = f"{record_map[SUBCATEGORY_NAME]}, has been Approved by the Admin"

                            message_sv = f"{record_map[SUBCATEGORY_NAME]}, har godkänts av eddi Admin. Klicka på länken"

                            receiver = [data.supplier.email_id]
                            send_notification(email_id, receiver, message)
                            # receiver_device_token = []
                            # device_data = UserDeviceToken.objects.filter(user_type=data.supplier)
                            # receiver_device_token.append(device_data.device_token)

                            # print(receiver_device_token)
                            # send_push_notification(receiver_device_token,message)
                            
                            for i in receiver:
                                try:
                                    record_map1 = {}
                                    record_map1 = {
                                        "sender" : email_id,
                                        "receiver" : i,
                                        "message" : message,
                                        "message_sv" : message_sv
                                    }

                                    getattr(models,"Notification").objects.update_or_create(**record_map1)
                                except:
                                    pass
                        except:
                            pass

                    if request.POST.get(APPROVAL_STATUS) == "Pending":
                        try:
                            data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{COURSE_CATEGORY:data.category_name})
                        except:
                            data1 = None
                        if data1.exists():
                            return Response({STATUS: ERROR, DATA: "Someone has already enrolled in this category", DATA_SV:"Någon har redan registrerat sig inom denna kategori, kategori kan inte raderas"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            record_map[IS_APPROVED_ID] = 2
                    if request.POST.get(APPROVAL_STATUS) == "Rejected":
                        try:
                            data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{COURSE_CATEGORY:data.category_name})
                        except:
                            data1 = None
                        if data1.exists():
                            return Response({STATUS: ERROR, DATA: "Someone has already enrolled in this category", DATA_SV:"Någon har redan registrerat sig inom denna kategori, kategori kan inte raderas"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            record_map[IS_APPROVED_ID] = 3
                            try:
                                message = f"Course SubCategory {record_map[SUBCATEGORY_NAME]}, has been Rejected by the Admin"

                                message_sv = f"Course SubCategory {record_map[SUBCATEGORY_NAME]}, has been Rejected by the Admin"

                                receiver = [data.supplier.email_id]
                                send_notification(email_id, receiver, message)
                                # receiver_device_token = []
                                # device_data = UserDeviceToken.objects.filter(user_type=data.supplier)
                                # receiver_device_token.append(device_data.device_token)

                                # print(receiver_device_token)
                                # send_push_notification(receiver_device_token,message)

                                for i in receiver:
                                    try:
                                        record_map2 = {}
                                        record_map2 = {
                                            "sender" : email_id,
                                            "receiver" : i,
                                            "message" : message,
                                            "message_sv" : message_sv
                                        }

                                        getattr(models,"Notification").objects.update_or_create(**record_map2)
                                    except:
                                        pass
                            except:
                                pass

                else:
                    record_map[IS_APPROVED] = data.is_approved

            elif user_type_data == SUPPLIER_S:
                if request.POST.get(STATUS):
                    if request.POST.get(STATUS) == "Active":
                        record_map[STATUS_ID] = 1
                    else:
                        try:
                            data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{COURSE_CATEGORY:data.category_name})
                        except:
                            data1 = None
                        if data1.exists():
                            return Response({STATUS: ERROR, DATA: "Someone already enrolled in this course", DATA_SV:"Någon har redan registrerat sig på denna utbildning"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            record_map[STATUS_ID] = 2
                else:
                    record_map[STATUS] = data.status
                    record_map[IS_APPROVED_ID] = 2

        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Information succesfully edited", DATA_SV:"Informationen är nu uppdaterad"}, status=status.HTTP_200_OK)

    def delete(self,request,uuid = None):
        email_id =  get_user_email_by_token(request)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({STATUS: SUCCESS, DATA: "Information succesfully deleted", DATA_SV:"Data har nu raderats"}, status=status.HTTP_200_OK)

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
        except:
            vat_val = None
        if uuid:
            email_id = get_user_email_by_token(request)
            # try:
            #     user = getattr(models,USER_PROFILE_TABLE).objects.get(**{"email_id":email_id})
            # except:
            #     user = None
            try:
                course_data = getattr(models,COURSEDETAILS_TABLE).objects.select_related('supplier').get(**{UUID:uuid, IS_DELETED:False})
                
            except:
                course_data = None
            print(course_data)
            try:
                supplier_profile = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{"supplier_email":course_data.supplier.email_id})
            except:
                supplier_profile = None
            print(supplier_profile)
            try:
                fav_data = getattr(models,FAVOURITE_COURSE_TABLE).objects.filter(**{COURSE:course_data}).get(**{EMAIL_ID:email_id})
                fav_dataa = fav_data.is_favourite
            except:
                fav_data = None
                fav_dataa = None

            try:
                user_data = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{COURSE:course_data, STATUS:"Success"}).values_list("email_id", flat=True)
                individuals = getattr(models,USER_PROFILE_TABLE).objects.filter(**{"email_id__in":user_data, IS_DELETED:False})
                lerner_count = len(individuals)
            except Exception as e:
                individuals = None
                lerner_count = None
            try:
                var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, COURSE:course_data, STATUS:"Success"})
            except:
                var = None
            var1 = True if var is not None else False

            try:
                rating = getattr(models,"CourseRating").objects.filter(**{COURSE_NAME:course_data})
                l = []
                for i in rating:
                    l.append(float(i.star))
                final_rating = "{:.1f}".format(sum(l)/len(l))
            except:
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
                if getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id}).user_type.user_type == SUPPLIER_S:
                    try:
                        data_s = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{'supplier__email_id':email_id, IS_DELETED:False}).order_by("-created_date_time")

                    except:
                        return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
                    if serializer := CourseDetailsSerializer(data_s,many=True):
                        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

                elif getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id, IS_DELETED:False}).user_type.user_type == ADMIN_S:
                    try:
                        data_a = getattr(models,COURSEDETAILS_TABLE).objects.all().order_by("-created_date_time")
                    except:
                        return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

                    if serializer := CourseDetailsSerializer(data_a,many=True):
                        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

                else:
                    try:
                        cat = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                    except:
                        return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
                    user_only_category = []
                    if cat.course_category != None:
                        try:
                            user_only_category = cat.course_category.split(",")
                        except Exception:
                           user_only_category = cat.course_category.split()
                    user_category = []
                    user_subcategory = []
                    try:
                        if cat.user_interests != None:
                            ab = json.loads(cat.user_interests)
                            for i in ab:
                                user_category.append(i["category"])
                                user_subcategory.append(i["subcategory"][0])
                    except:
                        pass
                    user_areaofinterest = []
                    if cat.area_of_interest != None:
                        try:
                            user_areaofinterest = cat.area_of_interest.split(",")
                        except:
                            user_areaofinterest = cat.area_of_interest.split()
                    

                    course_enrolled = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{EMAIL_ID:email_id}).values_list("course__course_name", flat=True)
                    print(course_enrolled, "enrolleddd")

                    user_profile_interest = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False}).filter(Q(course_subcategory__subcategory_name__in=user_areaofinterest + user_subcategory) | Q(course_category__category_name__in=user_areaofinterest + user_category + user_only_category)  | Q(course_name__in=user_areaofinterest)).exclude(course_name__in = course_enrolled)
                    print(user_profile_interest, "intererer")

                    target_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False, "course_for_organization" : True, "target_users__icontains" : email_id}).exclude(course_name__in = course_enrolled)

                    target_course_data = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False,"course_for_organization" : True, "target_users__icontains" : email_id}).exclude(course_name__in = course_enrolled).values_list("course_name")

                    print(target_course_data, "datata")

                    data_all = user_profile_interest.union(getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False, "course_for_organization" : False}).exclude(course_name__in = course_enrolled).exclude(course_name__in=target_course_data).exclude(course_name__in=user_profile_interest).order_by("-created_date_time"))

                if serializer := CourseDetailsSerializer(target_course,many=True):
                    if serializer_all := CourseDetailsSerializer(data_all, many=True):
                        return Response({STATUS: SUCCESS, DATA: serializer.data, "all_data": serializer_all.data}, status=status.HTTP_200_OK)
                    else:
                        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK) 
                else:
                    return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({STATUS: ERROR, DATA: "Token authentication required", DATA_SV:"Token auktorisering krävs"}, status=status.HTTP_400_BAD_REQUEST)
       

    def put(self,request,uuid = None):
        email_id =  get_user_email_by_token(request)
        try:
            user_type_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type
        except Exception:
            user_type_data = None
            
        res = None
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            enrolled = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{COURSE:data})
            if enrolled.exists():
                return Response({STATUS: ERROR, DATA: "Someone already enrolled in this course", DATA_SV:"Någon har redan registrerat sig på denna utbildning"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass
        try:
            category_id = getattr(models,COURSE_CATEGORY_TABLE).objects.only(ID).get(**{CATEGORY_NAME:request.POST.get(COURSE_CATEGORY_ID,data.course_category.category_name)})

            try:
                sub_category_id = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.only(ID).get(**{SUBCATEGORY_NAME:request.POST.get(SUBCATEGORY_NAME_ID,data.course_subcategory.subcategory_name)})
            except:
                sub_category_id = None

            course_type_id = getattr(models,COURSE_TYPE_TABLE).objects.only(ID).get(**{TYPE_NAME:request.POST.get(COURSE_TYPE_ID,data.course_type.type_name)})

            fee_type_id = getattr(models,FEE_TYPE_TABLE).objects.only(ID).get(**{FEE_TYPE_NAME :request.POST.get(FEE_TYPE_ID,data.fee_type.fee_type_name)})

            course_level_id = getattr(models,COURSE_LEVEL_TABLE).objects.only(ID).get(**{LEVEL_NAME : request.POST.get(COURSE_LEVEL_ID,data.course_level.level_name)})
        except:
            return Response({STATUS:ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {
            COURSE_IMAGE: request.FILES.get(COURSE_IMAGE,data.course_image),
            COURSE_NAME: request.POST.get(COURSE_NAME,data.course_name),
            COURSE_LEVEL_ID : course_level_id.id,
            COURSE_LENGTH : request.POST.get(COURSE_LENGTH,data.course_length),
            COURSE_CATEGORY_ID : category_id.id,
            COURSE_TYPE_ID : course_type_id.id,
            COURSE_LANGUAGE:request.POST.get(COURSE_LANGUAGE,data.course_language),
            ORGANIZATION_LOCATION: request.POST.get(ORGANIZATION_LOCATION,data.organization_location),
            COURSE_CHECKOUT_LINK: request.POST.get(COURSE_CHECKOUT_LINK,data.course_checkout_link),
            MEETING_LINK : request.POST.get(MEETING_LINK,data.meeting_link),
            MEETING_PASSCODE : request.POST.get(MEETING_PASSCODE,data.meeting_passcode),
            AUTHOR_NAME : request.POST.get(AUTHOR_NAME,data.author_name),
            AUTHOR_BIO : request.POST.get(MEETING_PASSCODE,data.author_bio),
            TARGET_USERS : request.POST.get(TARGET_USERS,data.target_users),
            FEE_TYPE_ID: fee_type_id.id,
            SUB_AREA:request.POST.get(SUB_AREA,data.sub_area),
            ADDITIONAL_INFORMATION: request.POST.get(ADDITIONAL_INFORMATION,data.additional_information),
        }
            if request.POST.get(COURSE_PRICE):
                record_map[COURSE_PRICE] = "{:.2f}".format(float(request.POST.get(COURSE_PRICE)))
            else:
                record_map[COURSE_PRICE] = data.course_price
            if request.POST.get("offer_price"):
                record_map["offer_price"] = "{:.2f}".format(float(request.POST.get("offer_price")))
            else:
                record_map["offer_price"] = data.offer_price
            if sub_category_id != None:
                record_map[COURSE_SUBCATEGORY_ID] = sub_category_id.id
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
                elif request.POST.get(COURSE_FOR_ORGANIZATION) == 'false':
                    record_map[COURSE_FOR_ORGANIZATION] = json.loads(request.POST.get(COURSE_FOR_ORGANIZATION))
                    record_map[ORGANIZATION_DOMAIN] = None
            else:
                record_map[COURSE_FOR_ORGANIZATION] = data.course_for_organization
                res = data.organization_domain

            if user_type_data != None:
                if user_type_data == ADMIN_S:
                    if request.POST.get(STATUS):
                        if request.POST.get(STATUS) == "Active":
                            record_map[STATUS_ID] = 1
                        else:
                            try:
                                data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__course__course_name":data.course_name})
                            except:
                                data1 = None
                            if data1.exists():
                                return Response({STATUS: ERROR, DATA: "Someone already enrolled in this course", DATA_SV:"Någon har redan registrerat sig på denna utbildning"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                record_map[STATUS_ID] = 2
                                try:
                                    html_path = INACTIVE_COURSE
                                    context_data = {"course_name":request.POST.get(COURSE_NAME,data.course_name)}
                                    email_html_template = get_template(html_path).render(context_data)
                                    email_from = settings.EMAIL_HOST_USER
                                    recipient_list = (data.supplier.email_id,)
                                    email_msg = EmailMessage('Welcome to Eddi',email_html_template,email_from,recipient_list)
                                    email_msg.content_subtype = 'html'
                                    path = 'eddi_app'
                                    img_dir = 'static'
                                    image = 'Logo.png'
                                    file_path = os.path.join(path,img_dir,image)
                                    with open(file_path,'rb') as f:
                                        img = MIMEImage(f.read())
                                        img.add_header('Content-ID', '<{name}>'.format(name=image))
                                        img.add_header('Content-Disposition', 'inline', filename=image)
                                    email_msg.attach(img)
                                    email_msg.send(fail_silently=False)
                                except:
                                    pass
                    else:
                        record_map[STATUS] = data.status
                        
                    if request.POST.get(APPROVAL_STATUS):
                        if request.POST.get(APPROVAL_STATUS) == "Approved":
                            record_map[IS_APPROVED_ID] = 1
                            try:
                                message = f"{record_map[COURSE_NAME]}, has been Approved by the Admin"
                                message_sv = f"{record_map[COURSE_NAME]}, har godkänts av Eddi Admin"
                                receiver = [data.supplier.email_id]
                                send_notification(email_id, receiver, message)
                                # receiver_device_token = []
                                # device_data = UserDeviceToken.objects.filter(user_type=data.supplier)
                                # receiver_device_token.append(device_data.device_token)

                                # print(receiver_device_token)
                                # send_push_notification(receiver_device_token,message)
                                for i in receiver:
                                    try:
                                        record_map1 = {}
                                        record_map1 = {
                                            "sender" : email_id,
                                            "receiver" : i,
                                            "message" : message,
                                            "message_sv" : message_sv
                                        }
                                        getattr(models,"Notification").objects.update_or_create(**record_map1)
                                    except:
                                        pass
                            except:
                                pass
                            try:
                                html_path = APPROVE_COURSE_HTML
                                context_data = {"supplier_name":f"{data.supplier.first_name} {data.supplier.last_name}","course_name":request.POST.get(COURSE_NAME,data.course_name)}
                                email_html_template = get_template(html_path).render(context_data)
                                email_from = settings.EMAIL_HOST_USER
                                recipient_list = (data.supplier.email_id,)
                                email_msg = EmailMessage('Course Approved by Admin',email_html_template,email_from,recipient_list)
                                email_msg.content_subtype = 'html'
                                path = 'eddi_app'
                                img_dir = 'static'
                                image = 'Logo.png'
                                file_path = os.path.join(path,img_dir,image)
                                with open(file_path,'rb') as f:
                                    img = MIMEImage(f.read())
                                    img.add_header('Content-ID', '<{name}>'.format(name=image))
                                    img.add_header('Content-Disposition', 'inline', filename=image)
                                email_msg.attach(img)
                                email_msg.send(fail_silently=False)
                            except:
                                pass

                        if request.POST.get(APPROVAL_STATUS) == "Pending":
                            try:
                                data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__course__course_name":data.course_name})
                            except:
                                data1 = None
                            if data1.exists():
                                return Response({STATUS: ERROR, DATA: "Someone already enrolled in this course", DATA_SV:"Någon har redan registrerat sig på denna utbildning"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                record_map[IS_APPROVED_ID] = 2
                        if request.POST.get(APPROVAL_STATUS) == "Rejected":
                            try:
                                data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__course__course_name":data.course_name})
                            except:
                                data1 = None
                            if data1.exists():
                                return Response({STATUS: ERROR, DATA: "Someone already enrolled in this course", DATA_SV:"Någon har redan registrerat sig på denna utbildning"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                record_map[IS_APPROVED_ID] = 3
                                try:
                                    message = f"{record_map[COURSE_NAME]}, has been Rejected by the Admin"
                                    message_sv = f"{record_map[COURSE_NAME]},har inte godkänts av Eddi Admin"
                                    receiver = [data.supplier.email_id]
                                    send_notification(email_id, receiver, message)
                                    # receiver_device_token = []
                                    # device_data = UserDeviceToken.objects.filter(user_type=data.supplier)
                                    # receiver_device_token.append(device_data.device_token)

                                    # print(receiver_device_token)
                                    # send_push_notification(receiver_device_token,message)
                                    for i in receiver:
                                        try:
                                            record_map2 = {}
                                            record_map2 = {
                                                "sender" : email_id,
                                                "receiver" : i,
                                                "message" : message,
                                                "message_sv" : message_sv
                                            }

                                            getattr(models,"Notification").objects.update_or_create(**record_map2)
                                        except:
                                            pass
                                except:
                                    pass
                    else:
                        record_map[IS_APPROVED] = data.is_approved

                elif user_type_data == SUPPLIER_S:
                    if request.POST.get(STATUS):
                        if request.POST.get(STATUS) == "Active":
                            record_map[STATUS_ID] = 1
                        else:
                            try:
                                data1 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__course__course_name":data.course_name})
                            except:
                                data1 = None
                            if data1.exists():
                                return Response({STATUS: ERROR, DATA: "Someone already enrolled in this course", DATA_SV:"Någon har redan registrerat sig på denna utbildning"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                record_map[STATUS_ID] = 2
                    else:
                        record_map[STATUS] = data.status
                        record_map[IS_APPROVED_ID] = 2
                record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
                record_map[MODIFIED_BY] = 'admin'
                for key,value in record_map.items():
                    setattr(data,key,value)
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Information successfully edited", DATA_SV:"Din information har nu ändrats"}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request,uuid = None):
        email_id =  get_user_email_by_token(request)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except Exception:
            return Response({STATUS: ERROR, DATA: "Requested data not found", DATA_SV:"Efterfrågad information kan inte hittas"}, status=status.HTTP_400_BAD_REQUEST)
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
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Information successfully deleted", DATA_SV:"Data har nu raderats"}, status=status.HTTP_200_OK)
    
class AdminDashboardView(APIView):
    def get(self, request,uuid = None):
        admin_email = get_user_email_by_token(request)
        data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:admin_email})
        if data.user_type.user_type == "Admin":
            try:
                total_supplier = getattr(models,USERSIGNUP_TABLE).objects.filter(**{USER_TYPE_ID:1}).count()
                total_user = getattr(models,USERSIGNUP_TABLE).objects.filter(**{USER_TYPE_ID:2}).count()
                total_course = getattr(models,COURSEDETAILS_TABLE).objects.all().count()
                purchased_course = getattr(models,COURSE_ENROLL_TABLE).objects.all().count()
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                users = getattr(models,USERSIGNUP_TABLE).objects.all().exclude(user_type_id = 3)
                course_supplier = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__user_type_id":1})
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            if serializer :=  UserSignupSerializer(users, many = True):
                if serializer1 := CourseDetailsSerializer ( course_supplier, many = True):
                    print(len(connection.queries))
                    return Response({STATUS: SUCCESS,
                "admin_name" : f"{data.first_name} {data.last_name}",
                "supplier_count": total_supplier,
                "user_count": total_user,
                "total_course": total_course,
                PURCHASED_COURSE_COUNT: purchased_course,
                "users": serializer.data,
                "suppliers": serializer1.data,
                }, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({STATUS: ERROR, DATA: "User is not authorized", DATA_SV:"Du kan inte utföra denna handling"}, status=status.HTTP_400_BAD_REQUEST)

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

        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Individuals11 = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email}).values_list("payment_detail__course__course_name",'user_profile__first_name','user_profile__email_id','user_profile__usersignup__uuid')
            
            course_name = [x[0] for x in Individuals11]
            user_name = [x[1] for x in Individuals11]
            user_email = [x[2] for x in Individuals11]
            user_uuid = [x[3] for x in Individuals11]
      
            individual_details = {}
            final_dict = {}
            individual_details[USERNAME] = user_name
            individual_details[COURSENAME] = course_name
            individual_details[USER_EMAIL] = user_email
            individual_details[USER_UUID] = user_uuid

            counter = 0
            for v in individual_details[COURSENAME]:
                Individuals = getattr(models,COURSEDETAILS_TABLE).objects.select_related('course_type').get(**{COURSE_NAME:v})
                final_dict[counter] = {
                    USERNAME:individual_details[USERNAME][counter],
                    USER_EMAIL:individual_details[USER_EMAIL][counter],
                    USER_UUID:individual_details[USER_UUID][counter],
                    COURSE_ID:str(Individuals.uuid),
                    COURSENAME:v,
                    COURSETYPE:Individuals.course_type.type_name,
                }
                counter +=1
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            all_subcategory = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False})
        except:
            all_subcategory = None
        try:
            if all_subcategory_serializer := SubCategoryDetailsSerializer(all_subcategory, many=True):
                newvar = all_subcategory_serializer.data
        except:
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
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
       

class SupplierDashboard_Active_InActiveView(APIView):
    def put(self,request):
        status_s = request.POST.get(STATUS)
        course_name = request.POST.get(COURSE_NAME)
        try:
            data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{COURSE_NAME:course_name})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {}
        record_map = {STATUS_ID: 1,} if status_s == "Active" else {STATUS_ID: 2,}

        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Information successfully edited", DATA_SV:"Din information har nu ändrats"}, status=status.HTTP_200_OK)



class SupplierDashboard_courseGraphView(APIView):
    def post(self, request):
        supplier_email = get_user_email_by_token(request)
        time_period = request.POST.get(TIME_PERIOD)
        date = datetime.datetime.now()

        if time_period == WEEKLY:
            week = date.strftime("%V")
            try:
                course_offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__week":week}).count()
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                purchased = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,'payment_detail__status':'Success',"created_date_time__week":week,}).values_list("payment_detail__course__course_name", flat=True)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            set1 = set(purchased)
            purchased_course = len(set1)
            try:
                all_supplier_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__week":week}).values_list(COURSE_NAME, flat=True)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

            set_all = set(all_supplier_course)
            non_purchased = len(set_all-set1)

        elif time_period == MONTHLY:
            month = date.strftime("%m")
            try:
                course_offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__month":month}).count()
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                purchased = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__month":month,'payment_detail__status':'Success'}).values_list("payment_detail__course__course_name", flat=True)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            set1 = set(purchased)
            purchased_course = len(set1)
            try:
                all_supplier_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__month":month}).values_list(COURSE_NAME, flat=True)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            set_all = set(all_supplier_course)
            non_purchased = len(set_all-set1)

        elif time_period == YEARLY:
            year = date.strftime("%Y")
            try:
                course_offered = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__year":year}).count()
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            try:

                purchased = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__year":year,'payment_detail__status':'Success'}).values_list("payment_detail__course__course_name", flat=True)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            set1 = set(purchased)
            purchased_course = len(set1)
            try:
                all_supplier_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":supplier_email,"created_date_time__year":year}).values_list(COURSE_NAME, flat=True)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
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
                    final = "{:.2f}".format(sum(var))
                    if var == "":
                        final = 0.0
                    week_list[past.strftime("%A")] = final
                data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{SUPPLIER_EMAIL:supplier_email,"created_date_time__week":week}).values_list("payment_detail__amount", flat=True)
                total_earning = "{:.2f}".format(sum(list(data)))
                return Response({STATUS: SUCCESS,"total_earning": total_earning, DATA:week_list}, status=status.HTTP_200_OK)
            except: 
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

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

                total_earning = "{:.2f}".format(sum(list(data)))
                return Response({STATUS: SUCCESS,"total_earning": total_earning, DATA:month_list}, status=status.HTTP_200_OK)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        
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
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

class CourseMaterialUpload(APIView):
    def post(self, request, uuid=None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                course_data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{UUID:uuid})
            except:
                 return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            reccord_map = {}
            reccord_map = {
                "course_id" : course_data.id
                }
            data = getattr(models,"CourseMaterial").objects.update_or_create(**reccord_map)
            for i in range(1,int(request.POST.get("new_document_count"))+1):
                try:
                    data1 = getattr(models,"MaterialDocumentMaterial").objects.update_or_create(**{"document_file":request.FILES.get('document_file_'f'{i}'), "file_name":request.POST.get('document_title_'f'{i}')})
                    data[0].document_files.add(data1[0].id)
                except:
                    return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                for j in range(1,int(request.POST.get("new_video_count"))+1):
                    data2 = getattr(models,"MaterialVideoMaterial").objects.update_or_create(**{"video_file":request.FILES.get('video_file_'f'{j}'), "video_name":request.POST.get('video_title_'f'{j}')})
                    data[0].video_files.add(data2[0].id)
                    try:
                        live_path = "/var/www/html/eddi-backend/media/"
                        actual_path = live_path+str(data2[0].video_file)
                        video = cv2.VideoCapture(actual_path)
                        video.set(cv2.CAP_PROP_POS_AVI_RATIO,1)
                        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
                        fps = int(video.get(cv2.CAP_PROP_FPS))
                        seconds = int(frame_count / fps)
                        video_time = str(timedelta(seconds=seconds))
                        data2[0].actual_duration = video_time
                        data2[0].save()
                    except:
                        pass
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)      
        return Response({STATUS: SUCCESS, DATA: "Course material uploaded successfully", DATA_SV:"Utbildningsunderlag är nu upplagda"}, status=status.HTTP_200_OK)
    
    def get(self,request, uuid=None):
        if uuid:
            video = []
            try:
                try:
                    course_material_data = getattr(models,"CourseMaterial").objects.get(**{"course__uuid":uuid})
                    all_video_data = course_material_data.video_files.all()
                except:
                    course_material_data = None
                for i in all_video_data:
                    try:
                        course_material_status = getattr(models,"CourseMaterialStatus").objects.get(**{'video_id':i.uuid})
                        video.append(course_material_status)
                    except:
                        course_material_status = None
                course_material_final_video = getattr(models,"CourseMaterialStatus").objects.filter(**{'video_id__in':video})
            except:
                course_material_final_video = None
            if serializer := CourseMaterialSerializer(course_material_data):
                if serializer1 := CourseMaterialStatusSerializer(course_material_final_video, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data, "material_status":serializer1.data}, status=status.HTTP_200_OK)
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, uuid=None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        course_material_data = getattr(models,"CourseMaterial").objects.get(**{"course__uuid":uuid})
        video_files_old = request.POST.getlist("video_files_old",None)
        document_files_old = request.POST.getlist("document_files_old",None)
        try:
            old_docs = course_material_data.document_files.all()
            old_docs_list = list(old_docs)
            oldd = [i.document_file.url for i in old_docs_list]
            for i in document_files_old:
                l = i.split(",")
                if l[0] in oldd:
                    var = getattr(models,"MaterialDocumentMaterial").objects.get(**{"document_file":l[0][7:]})
                    var.file_name = l[1]
                    var.save()
                     # removing already existing doc from the list oldd
                    oldd.remove(l[0])
            for k in oldd:
                try:
                    getattr(models,"MaterialDocumentMaterial").objects.get(**{"document_file":k[7:]}).delete()
                except:
                    pass
            if int(request.POST.get("new_document_count")) > 0:
                for j in range(1,int(request.POST.get("new_document_count"))+1):
                    data1 = getattr(models,"MaterialDocumentMaterial").objects.update_or_create(**{"document_file":request.FILES.get('document_file_'f'{j}'), "file_name":request.POST.get('document_title_'f'{j}')})
                    course_material_data.document_files.add(data1[0].id)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            old_videos = course_material_data.video_files.all()
            old_videos_list = list(old_videos)
            oldd1 = [i.video_file.url for i in old_videos_list]
            for i in video_files_old:
                l = i.split(",")
                if l[0] in oldd1:
                    var = getattr(models,"MaterialVideoMaterial").objects.get(**{"video_file":l[0][7:]})
                    var.video_name = l[1]
                    var.save()
                    # removing already existing videos from the list oldd1
                    oldd1.remove(l[0])
            for j in oldd1:
                try:
                    getattr(models,"MaterialVideoMaterial").objects.get(**{"video_file":j[7:]}).delete()
                except:
                    pass
            if int(request.POST.get("new_video_count")) > 0:
                for j in range(1,int(request.POST.get("new_video_count"))+1):
                    data1 = getattr(models,"MaterialVideoMaterial").objects.update_or_create(**{"video_file":request.FILES.get('video_file_'f'{j}'), "video_name":request.POST.get('video_title_'f'{j}')})
                    course_material_data.video_files.add(data1[0].id)
                    try:
                        live_path = "/var/www/html/eddi-backend/media/"
                        actual_path = live_path+str(data1[0].video_file)
                        video = cv2.VideoCapture(actual_path)
                        video.set(cv2.CAP_PROP_POS_AVI_RATIO,1)
                        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
                        fps = int(video.get(cv2.CAP_PROP_FPS))
                        seconds = int(frame_count / fps)
                        video_time = str(timedelta(seconds=seconds))
                        data1[0].actual_duration = video_time
                        data1[0].save()
                    except:
                        pass
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)      
        return Response({STATUS: SUCCESS, DATA: "Material edited successfully", DATA_SV:"Utbildningsunderlag är nu uppdaterade"}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class SupplierOrganizationProfileviewall(APIView):
    def get(self, request):
        try:
            all_supplier = getattr(models,USERSIGNUP_TABLE).objects.filter(**{"user_type__user_type" : SUPPLIER_S}).values_list('email_id', flat=True)
            data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.filter(**{"supplier_email__in":all_supplier})
        except:
            data= None
        if serializer := SupplierOrganizationProfileSerializer(data, many=True):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SupplierOrganizationProfileAdminview(APIView):
    def post(self, request):
        supplier_email = request.POST.get("supplier_email")
        if request.POST.get("supplier_email"):
            try:
                data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:supplier_email})
            except:
                data= None
            try:
                user_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:supplier_email})
            except:
                user_data= None
            if serializer := SupplierOrganizationProfileSerializer(data):
                if serializer1 := UserSignupSerializer(user_data):
                    return Response({STATUS: SUCCESS, DATA: serializer.data, "supplier_info":serializer1.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.all()
        except:
            data= None
        if serializer := SupplierOrganizationProfileSerializer(data, many=True):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class SupplierOrganizationProfileview(APIView):
    def post(self, request):
        email_id = get_user_email_by_token(request)
        usersignup_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
        try:
            record_map = {
                SUPPLIER_EMAIL : email_id,
                "usersignup":usersignup_data,
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
                "linkedIn_profile" : request.POST.get("linkedIn_profile",None),
                "facebook_profile" : request.POST.get("facebook_profile",None),
                ORGANIZATION_LOGO : request.FILES.get(ORGANIZATION_LOGO,None),
            }
            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[IS_APPROVED_ID] = 2
            record_map[STATUS_ID] = 2 
            try:
                getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.update_or_create(**record_map)
                try:
                    # data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
                    html_path = "supplier_organization_approval.html"
                    fullname = f'{usersignup_data.first_name} {usersignup_data.last_name}'
                    context_data = {'fullname':fullname}
                    email_html_template = get_template(html_path).render(context_data)
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = (email_id,)
                    email_msg = EmailMessage('Profile Created Successfully',email_html_template,email_from,recipient_list)
                    email_msg.content_subtype = 'html'
                    path = 'eddi_app'
                    img_dir = 'static'
                    image = 'Logo.png'
                    file_path = os.path.join(path,img_dir,image)
                    with open(file_path,'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-ID', '<{name}>'.format(name=image))
                        img.add_header('Content-Disposition', 'inline', filename=image)
                    email_msg.attach(img)
                    email_msg.send(fail_silently=False)
                except:
                    pass
                try:
                    # data1 = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
                    usersignup_data.is_resetpassword = False
                    usersignup_data.is_first_time_login = False
                    usersignup_data.save()
                except Exception as ex:
                    pass
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Profile created successfully. Your profile is under review by admin", DATA_SV:"Din profil är nu skapad,och granskas av admin"}, status=status.HTTP_200_OK)


    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except:
            data= None
        try:
            user_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
        except:
            user_data= None

        if serializer := SupplierOrganizationProfileSerializer(data):
            if serializer1 := UserSignupSerializer(user_data):
                return Response({STATUS: SUCCESS, DATA: serializer.data, "supplier_info":serializer1.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request):
        email_id = get_user_email_by_token(request)
        supplier_email = request.POST.get("supplier_email")
        print(supplier_email,"supplierererer")
        data =  getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
        if data.user_type.user_type == ADMIN_S:
            data1 = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:supplier_email})
            record_map1 = {}
            if request.POST.get(STATUS):
                if request.POST.get(STATUS) == "Active":
                    record_map1[STATUS_ID] = 1
                    try:
                        # data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
                        html_path = "supplier_active.html"
                        fullname = f'{data1.usersignup.first_name} {data1.usersignup.first_name}'
                        context_data = {'fullname':fullname, "email_id":email_id}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (data1.supplier_email,)
                        email_msg = EmailMessage('Account has been Activated by the Admin',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        path = 'eddi_app'
                        img_dir = 'static'
                        image = 'Logo.png'
                        file_path = os.path.join(path,img_dir,image)
                        with open(file_path,'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', '<{name}>'.format(name=image))
                            img.add_header('Content-Disposition', 'inline', filename=image)
                        email_msg.attach(img)
                        email_msg.send(fail_silently=False)
                    except:
                        pass
                else:
                    record_map1[STATUS_ID] = 2
                    try:
                        # data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
                        html_path = "supplier_inactive.html"
                        fullname = f'{data1.usersignup.first_name} {data1.usersignup.last_name}'
                        context_data = {'fullname':fullname, "email_id":email_id}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (data1.supplier_email,)
                        email_msg = EmailMessage('Account has been Deactivated by the Admin',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        path = 'eddi_app'
                        img_dir = 'static'
                        image = 'Logo.png'
                        file_path = os.path.join(path,img_dir,image)
                        with open(file_path,'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', '<{name}>'.format(name=image))
                            img.add_header('Content-Disposition', 'inline', filename=image)
                        email_msg.attach(img)
                        email_msg.send(fail_silently=False)
                    except:
                        pass
            else:
                record_map1[STATUS] = data1.status

            if request.POST.get(APPROVAL_STATUS):
                if request.POST.get(APPROVAL_STATUS) == "Approved":
                    record_map1[IS_APPROVED_ID] = 1
                    record_map1[STATUS_ID] = 1
                    data1.rejection_count = 0
                    data1.approved_once = True
                    data1.save()
                    try:
                        # data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
                        html_path = "supplier_organization_approved.html"
                        fullname = f'{data1.usersignup.first_name} {data1.usersignup.last_name}'
                        context_data = {'fullname':fullname, "email_id":email_id}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (data1.supplier_email,)
                        email_msg = EmailMessage('Profile Approved by Admin',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        path = 'eddi_app'
                        img_dir = 'static'
                        image = 'Logo.png'
                        file_path = os.path.join(path,img_dir,image)
                        with open(file_path,'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', '<{name}>'.format(name=image))
                            img.add_header('Content-Disposition', 'inline', filename=image)
                        email_msg.attach(img)
                        email_msg.send(fail_silently=False)
                    except Exception as e:
                        print(e)
                        pass
                elif request.POST.get(APPROVAL_STATUS) == "Pending":
                    record_map1[IS_APPROVED_ID] = 2
                else:
                    record_map1[IS_APPROVED_ID] = 3
                    print("herererer")
                    data1.rejection_count += 1
                    data1.save()
                    if request.POST.get("reject_reason"):
                        record_map1["reject_reason"] = request.POST.get("reject_reason")
                    try:
                        # data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
                        html_path = "supplier_organization_reject.html"
                        fullname = f'{data.first_name} {data.last_name}'
                        context_data = {'fullname':fullname, "email_id":email_id, "reason":request.POST.get("reject_reason")}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (email_id,)
                        email_msg = EmailMessage('Profile Rejected by Admin',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        path = 'eddi_app'
                        img_dir = 'static'
                        image = 'Logo.png'
                        file_path = os.path.join(path,img_dir,image)
                        with open(file_path,'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', '<{name}>'.format(name=image))
                            img.add_header('Content-Disposition', 'inline', filename=image)
                        email_msg.attach(img)
                        email_msg.send(fail_silently=False)
                    except:
                        pass
                    
            else:
                record_map1[IS_APPROVED] = data1.is_approved
            for key,value in record_map1.items():
                setattr(data1,key,value)
            data1.save()
            return Response({STATUS: SUCCESS, DATA: "Information successfully edited", DATA_SV:"Din information har nu ändrats"}, status=status.HTTP_200_OK)

        try:
            data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

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
                "linkedIn_profile" : request.POST.get("linkedIn_profile",data.linkedIn_profile),
                "facebook_profile" : request.POST.get("facebook_profile",data.facebook_profile),
            }
            record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
            record_map[IS_APPROVED_ID] = 2
            record_map[STATUS_ID] = 2
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()            
            return Response({STATUS: SUCCESS, DATA: "Information successfully edited", DATA_SV:"Din information har nu ändrats"}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


class SupplierProfileView(APIView):
    def put(self, request):
        email_id = get_user_email_by_token(request)

        try:
            data = getattr(models,SUPPLIER_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except:
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
                return Response({STATUS: SUCCESS, DATA: "Profile data updated successfully", DATA_SV:"Profilinformation har nu uppdaterats"}, status=status.HTTP_200_OK)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({STATUS: SUCCESS, DATA: "Information successfully edited", DATA_SV:"Din information har nu ändrats"}, status=status.HTTP_200_OK)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


    
    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,SUPPLIER_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except:
            return Response({STATUS: ERROR, DATA:"Data not found", DATA_SV:"Ingen information tillgänglig"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer := SupplierProfileSerializer(data):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class MyProgressView(APIView):
    def get(self, request, uuid=None):
        email_id = get_user_email_by_token(request)
        is_completed_count = 0
        is_ongoing_count = 0
        try:
            enroll_data = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{'email_id':email_id}).values_list("course__course_name", flat = True)
        except:
            enroll_data = None
        try:
            course_data_uuid = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{'course_name__in':enroll_data}).values_list('uuid', flat=True).order_by("-created_date_time")
            
        except:
            course_data_uuid = None

        try:
            for i in list(course_data_uuid): 
                try:
                    var = getattr(models,"CourseMaterial").objects.get(**{'course__uuid':i})
                    all_videos = var.video_files.all()
                except:

                    var = None
                    is_ongoing_count += 1
                    continue
                l1 = []
                for j in all_videos:
                    try:
                        material_status = getattr(models,"CourseMaterialStatus").objects.get(**{'user_email':email_id, 'video_id':j.uuid})
                        l1.append(material_status.is_complete)
                    except:
                        pass
                if len(l1) != len(all_videos) or False in l1:
                    is_ongoing_count += 1
                else:
                    is_completed_count += 1            
            return Response({STATUS: SUCCESS, "is_completed_count":is_completed_count, "is_ongoing_count":is_ongoing_count}, status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex,"exexe")
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

class GetCourseListView(APIView):
    def get(self, request):
        email_id =  get_user_email_by_token(request)
        if getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id}).user_type.user_type == SUPPLIER_S or ADMIN_S:
            try:
                data_s = list(getattr(models,COURSEDETAILS_TABLE).objects.filter(**{'supplier__email_id':email_id, IS_DELETED:False, IS_APPROVED_ID:1,STATUS:1}).values_list("uuid","id","course_name").order_by("-created_date_time"))

            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({STATUS: SUCCESS, DATA:data_s}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

class CourseRatingAdmin(APIView):
    def get(self, request, uuid = None):
        email_id = get_user_email_by_token(request)
        user_data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
        if user_data.user_type.user_type == ADMIN_S:
            if uuid:
                try:
                    rating_data = getattr(models,"CourseRating").objects.get(**{UUID:uuid})
                    if serializer := CourseRatingSerializer(rating_data):
                        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                    else: 
                        return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)   
                except:
                    return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)   
            try:
                rating_data = getattr(models,"CourseRating").objects.all()
                if serializer := CourseRatingSerializer(rating_data,many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)   
        else:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen",'error':'not authorize'}, status=status.HTTP_400_BAD_REQUEST)
        

class AddBatchView(APIView):
    def post(self, request):
        email_id =  get_user_email_by_token(request)
        user_data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
        if user_data.user_type.user_type == SUPPLIER_S or ADMIN_S:
            if request.POST.get(BATCH_NAME):
                try:
                    batch_data = getattr(models,COURSE_BATCH).objects.get(**{"batch_name":request.POST.get(BATCH_NAME)})
                except Exception as ex:
                    batch_data = None
                if batch_data != None:
                    return Response({STATUS: ERROR, DATA: "Please choose unique batch name"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                record_map = {
                    BATCH_NAME : request.POST.get('batch_name'),
                    COURSE : getattr(models,COURSEDETAILS_TABLE).objects.get(**{'course_name':request.POST.get('course')}),
                    CREATED_AT : make_aware(datetime.datetime.now()),
                    CREATED_BY : user_data.user_type.user_type,
                    STATUS_ID:1
                }
                data = getattr(models,COURSE_BATCH).objects.update_or_create(**record_map)
               
                for i in request.POST.get('students').split(','):      
                    try:
                        data1 = getattr(models,USERPROFILE).objects.get(**{'usersignup__email_id':i})
                        data[0].students.add(data1.id)
                    
                    except Exception as ex:
                       print(ex)
                       return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen", 'error':str(ex)}, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({STATUS: SUCCESS, DATA: "Batch created successfully"}, status=status.HTTP_200_OK)
            
            except Exception as ex:
                print(ex)
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen", 'error':str(ex)}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen",'error':'not authorize'}, status=status.HTTP_400_BAD_REQUEST)

class GetBatchView(APIView):
    def get(self, request, uuid = None):
        if uuid:
            email_id =  get_user_email_by_token(request)
            try:
                batch_data = getattr(models,COURSE_BATCH).objects.select_related('course').get(**{UUID:uuid, IS_DELETED:False})
                if serializer := BatchDetailsSerializer(batch_data):
                    return Response({STATUS: SUCCESS, DATA:serializer.data}, status=status.HTTP_200_OK)

            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            email_id =  get_user_email_by_token(request)
            try:
                batch_data = getattr(models,COURSE_BATCH).objects.select_related('course').filter(**{'course__supplier__email_id':email_id,IS_DELETED:False})
                if serializer := BatchDetailsSerializer(batch_data,many=True):
                    return Response({STATUS: SUCCESS, DATA:serializer.data}, status=status.HTTP_200_OK)

            except Exception as ex:
                print(ex)
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, uuid = None):
        email_id =  get_user_email_by_token(request)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "UUID is required"}, status=status.HTTP_400_HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSE_BATCH).objects.get(**{UUID:uuid,STATUS:1})
            record_map = {
                    BATCH_NAME : request.POST.get('batch_name',data.batch_name),
                    MODIFIED_AT: make_aware(datetime.datetime.now()),
                    MODIFIED_BY: email_id,
                    STATUS: request.POST.get(STATUS,data.status)
                }
            if record_map[STATUS] == "Active":
                record_map[STATUS_ID] = 1
            elif record_map[STATUS] == "InActive":
                record_map[STATUS_ID] = 2
          
            record_map[COURSE] =  getattr(models,COURSEDETAILS_TABLE).objects.get(**{'course_name':request.POST.get('course')}) if request.POST.get('course') else data.course
          
            students_data = request.POST.get('students',None)

            if students_data:
                data.students.clear()
                for i in request.POST.get('students').split(','):    
                    try:
                        data1 = getattr(models,USERPROFILE).objects.get(**{'usersignup__email_id':i})
                        print(data1)
                        data.students.add(data1.id)    
                    except Exception as ex:
                        print(ex)
                        return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            
            
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()
            return Response({STATUS: SUCCESS, DATA: "Batch updated successfully"}, status=status.HTTP_200_OK)
       
        except Exception as ex:
            print(ex,"dasdasdasdexxxx")
            return Response({STATUS: ERROR, DATA: "Data not found"}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request,uuid = None):
        email_id =  get_user_email_by_token(request)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "UUID is required"}, status=status.HTTP_400_HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,COURSE_BATCH).objects.get(**{UUID:uuid,STATUS:1})
        except Exception as ex:
            print(ex)
            return Response({STATUS: ERROR, DATA: "Data not found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            STATUS_ID:2,
            IS_DELETED:True
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = email_id
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data succesfully deleted"}, status=status.HTTP_200_OK)

class AddSessionView(APIView):
    def post(self, request):
        email_id =  get_user_email_by_token(request)
        user_data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
        if user_data.user_type.user_type == SUPPLIER_S or ADMIN_S:
            if request.POST.get(SESSION_NAME):
                try:
                    session_data = getattr(models,BATCH_SESSION).objects.get(**{"session_name":request.POST.get(SESSION_NAME)})
                except Exception as ex:
                    session_data = None
                if session_data != None:
                    return Response({STATUS: ERROR, DATA: "Please choose unique session name"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    record_map = {
                        SESSION_NAME:request.POST.get(SESSION_NAME),
                        BATCH: getattr(models,COURSE_BATCH).objects.get(**{BATCH_NAME:request.POST.get(BATCH_NAME)}),
                        START_DATE: request.POST.get(START_DATE),
                        END_DATE: request.POST.get(END_DATE),
                        START_TIME:request.POST.get(START_TIME),
                        TOTAL_DURATION : request.POST.get(TOTAL_DURATION,None),
                        END_TIME:request.POST.get(END_TIME),
                        CHOOSE_DAYS:request.POST.get(CHOOSE_DAYS),
                        EVENT_ID:request.POST.get(EVENT_ID),
                        URL:request.POST.get(URL),
                        CUSTOM_DAYS:request.POST.get('custom_days'),
                        MODIFIED_AT: make_aware(datetime.datetime.now()),
                        MODIFIED_BY: email_id,
                    }
                    getattr(models,BATCH_SESSION).objects.update_or_create(**record_map)
                    return Response({STATUS: SUCCESS, DATA: "Session created successfully"}, status=status.HTTP_200_OK)
                
                except Exception as ex:
                    print(ex)
                    return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen",'error':'not authorize'}, status=status.HTTP_400_BAD_REQUEST)


class GetSessionView(APIView):
    def get(self, request, uuid = None):
        if uuid:
            email_id =  get_user_email_by_token(request)
            try:
                session_data = getattr(models,BATCH_SESSION).objects.select_related('batch').get(**{UUID:uuid, IS_DELETED:False})
                if serializer := SessionDetailsSerializer(session_data):
                    return Response({STATUS: SUCCESS, DATA:serializer.data}, status=status.HTTP_200_OK)

            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            email_id =  get_user_email_by_token(request)
            try:
                session_data = getattr(models,BATCH_SESSION).objects.select_related('batch').filter(**{'batch__course__supplier__email_id':email_id,IS_DELETED:False})
                if serializer := SessionDetailsSerializer(session_data,many=True):
                    return Response({STATUS: SUCCESS, DATA:serializer.data}, status=status.HTTP_200_OK)

            except Exception as ex:
                print(ex)
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, uuid = None):
        email_id =  get_user_email_by_token(request)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "UUID is required"}, status=status.HTTP_400_HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,BATCH_SESSION).objects.get(**{UUID:uuid})
        except Exception as ex:
            print(ex)
            return Response({STATUS: ERROR, DATA: "Data not found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            SESSION_NAME:request.POST.get(SESSION_NAME,data.session_name),
            BATCH: getattr(models,COURSE_BATCH).objects.get(**{BATCH_NAME:request.POST.get(BATCH_NAME)}) if request.POST.get('batch_name') else data.batch,
            START_DATE: request.POST.get(START_DATE,data.start_date),
            END_DATE: request.POST.get(START_DATE,data.end_date),
            START_TIME:request.POST.get(START_TIME,data.start_time),
            TOTAL_DURATION : request.POST.get(TOTAL_DURATION,data.total_duration),
            END_TIME:request.POST.get(END_TIME,data.end_time),
            CHOOSE_DAYS:request.POST.get(CHOOSE_DAYS,data.choose_days),
            EVENT_ID:request.POST.get(EVENT_ID,data.event_id),
            URL:request.POST.get(URL,data.url),
            CUSTOM_DAYS:request.POST.get('custom_days',data.customDays),
        }

        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Session updated successfully"}, status=status.HTTP_200_OK)

    def delete(self, request,uuid = None):
        email_id =  get_user_email_by_token(request)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "UUID is required"}, status=status.HTTP_400_HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,BATCH_SESSION).objects.get(**{UUID:uuid})
        except Exception as ex:
            print(ex)
            return Response({STATUS: ERROR, DATA: "Data not found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            IS_DELETED:True
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = email_id
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data succesfully deleted"}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class SaveStripeAccount(APIView):
    def post(self,request, uuid = None):
        try:
            auth_code = request.POST.get('auth_code')
            stripe_response = stripe.OAuth.token(
                grant_type = 'authorization_code',
                code = auth_code
            )
            if stripe_response['stripe_user_id']:
                try:
                    supplier_account = stripe.Account.retrieve(stripe_response['stripe_user_id'])
                    record_map = {
                        'supplier' : getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:supplier_account['email']}),
                        'account_id' : stripe_response['stripe_user_id']
                    }
                    print(record_map)
                    getattr(models,"SupplierAccountDetail").objects.update_or_create(**record_map)
                    return Response({STATUS: SUCCESS, DATA: "Account  Connected Succesfully"}, status=status.HTTP_200_OK)
               
                except Exception as ex:
                    print(ex)
                    return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({STATUS: SUCCESS, DATA: stripe_response}, status=status.HTTP_200_OK)
        
        except Exception as ex:
            print(ex)
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


class GetAdminPaymentList(APIView):
    def get(self,request, uuid=None):
        email_id =  get_user_email_by_token(request)
        user_data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
        if user_data.user_type.user_type == ADMIN_S:
            if uuid :
                payment_detail = getattr(models,"SupplierAccountDetail").objects.get(**{UUID:uuid})
                if serializer := SupplierAccountDetailSerializer(payment_detail):
                    return Response({STATUS: SUCCESS, DATA:serializer.data}, status=status.HTTP_200_OK)
            else:
                payment_list = getattr(models,"SupplierAccountDetail").objects.all()
                if serializer := SupplierAccountDetailSerializer(payment_list,many=True):
                    return Response({STATUS: SUCCESS, DATA:serializer.data}, status=status.HTTP_200_OK)

        else:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen",'error':'not authorize'}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class GetAccountDetail(APIView):
    def get(self,request):
        try:
            email = "kabariyanishant@gmail.com"
            supplier_account = getattr(models,"SupplierAccountDetail").objects.get(**{'supplier__email_id':email})
            print(supplier_account.account_id)
            balance = stripe.Balance.retrieve(
                stripe_account=supplier_account.account_id
            )
            print(balance)
        
        except Exception as ex:
            print(ex)
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


class SupplierWithDrawRequest(APIView):
    def post(self,request):
        try:
            email_id =  get_user_email_by_token(request)
            user_data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
            if user_data.user_type.user_type == SUPPLIER_S:
                try:
                    supplier_data = getattr(models,"SupplierAccountDetail").objects.get(**{'supplier__email_id':email_id})
                except Exception:
                    return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
                withdraw_amount = float(request.POST.get('amount'))
               
                if withdraw_amount <= supplier_data.total_amount_due:
                        html_path = RESETPASSWORD_HTML
                        fullname = supplier_data.supplier.first_name + " " + supplier_data.supplier.last_name
                        context_data = {"amount": withdraw_amount,"fullname":fullname}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (email_id,)
                        email_msg = EmailMessage('Supplier Request to Withdraw the Amount',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        path = 'eddi_app'
                        img_dir = 'static'  
                        image = 'Logo.png'
                        file_path = os.path.join(path,img_dir,image)
                        with open(file_path,'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', '<{name}>'.format(name=image))
                            img.add_header('Content-Disposition', 'inline', filename=image)
                        email_msg.attach(img)
                        email_msg.send(fail_silently=False)
                        return Response({STATUS: SUCCESS, DATA: "Email sent successfully"}, status=status.HTTP_200_OK) 
                else:
                    return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            print(ex)
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
    

class SupplierPayout(APIView):
    def post(self, request, uuid=None):
        try:
            email_id = get_user_email_by_token(request)
            user_data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
            if user_data.user_type.user_type == ADMIN_S:
                amount = request.POST.get(AMOUNT)  
                supplier_account = getattr(models,"SupplierAccountDetail").objects.get(**{"supplier__uuid":uuid})
                if amount <= supplier_account.total_amount_due:
                    payout = stripe.Payout.create(
                        amount=int(amount)*100,
                        currency='sek',
                        stripe_account=supplier_account.account_id,
                    )
                    print(payout)

        except Exception as ex:
            print(ex)
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST) 