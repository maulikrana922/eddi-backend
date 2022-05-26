from email.mime.image import MIMEImage
import os
from xhtml2pdf import pisa
import requests
import random
from random import shuffle
from io import BytesIO
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from eddi_app.permissions import IsValid
from .serializers import *
from eddi_app import models
from eddi_app.constants.constants import *
from eddi_app.constants.table_name import *
import datetime
from datetime import date
from django.db.models import Q
from collections import OrderedDict
import pdfkit
from django.utils.timezone import make_aware
from django.contrib.auth.hashers import make_password, check_password
from .supplier_views import *
from uuid import uuid4
import stripe # 2.68.0
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from moviepy.editor import VideoFileClip
import datetime
from django.core import mail
from django.template.loader import render_to_string
from django.core.mail import get_connection, EmailMultiAlternatives


stripe.api_key = settings.STRIPE_SECRET_KEY

def send_notification(sender, receiver, message, sender_type=None, receiver_type=None):

    url = "https://testyourapp.online:5001"
    payload = json.dumps({
    "type": "type1",
    "json": {
        'sender': sender,
        'receiver': receiver,
        # "sender_type": sender_type,
        # "receiver_type" : receiver_type,
        "message": message,
        "time" : datetime.datetime.now()
    }
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

@permission_classes([AllowAny])
class Save_stripe_info(APIView):
    def post(self, request, *args, **kwargs):
        if request.method == POST_METHOD:
            email_id = request.POST.get(EMAIL_ID)
            amount = request.POST.get(PRICE)
            payment_method_id = request.POST.get(PAYMENT_METHOD_ID)
            course_name = request.POST.get(COURSE_NAME)
            extra_msg = ''
            try:
                var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, COURSE_NAME:course_name,STATUS:'Success'})
                if var is not None:
                    return Response({MESSAGE: ERROR, DATA: "You already Enrolled"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                pass
            
            try:
                customer_data = stripe.Customer.list(email=email_id).data
                if len(customer_data) == 0:
                    # creating customer
                    customer = stripe.Customer.create(email=email_id, payment_method=payment_method_id)
                else:
                    customer = customer_data[0]
                    extra_msg = "Customer already existed."
                    
                # creating paymentIntent
                try:
                    intent = stripe.PaymentIntent.create(
                    amount=int(amount)*100,
                    currency='usd',
                    description='helllo',
                    customer=customer['id'],
                    payment_method_types=["card"],
                    payment_method=payment_method_id,
                    confirm=True)

                except Exception as e:
                    pass
                try:
                    instance = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                    vat = getattr(models,"InvoiceVATCMS").objects.all().values_list("vat_value", flat=True)
                    vat_val = int(vat[0])
                    html_path = COURSE_ENROLL_HTML_TO_U
                    fullname = f'{instance.first_name} {instance.last_name}'
                    context_data = {'fullname':fullname, "course_name":course_name}
                    email_html_template = get_template(html_path).render(context_data)
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = (instance.email_id,)
                    invoice_number = random.randrange(100000,999999)
                    context_data1 = {"invoice_number":invoice_number,"user_address":"User Address","issue_date":date.today(),"course_name":course_name,"course_fees": amount, "vat":vat_val, "total":int(amount) + (int(amount)*vat_val)/100}
                    template = get_template('invoice.html').render(context_data1)
                    try: 
                        result = BytesIO()
                        pdf = pisa.pisaDocument(BytesIO(template.encode("UTF-8")), result)#, link_callback=fetch_resources)
                        pdf = result.getvalue()
                        filename = f'Invoice-{invoice_number}.pdf'
                    except Exception as ex:
                        pass
                    record = {}
                    try:
                        record = {
                        "invoice_number" : invoice_number,
                        "user_address" : "Address",
                        "user_email" : instance.email_id,
                        "course_name" : course_name,
                        "vat_charges" : vat_val
                        }
                        getattr(models,"InvoiceData").objects.update_or_create(**record)
                    except Exception as ex:
                        pass
                    try:
                        path = 'eddi_app'
                        img_dir = 'static'
                        image = 'Logo.jpg'
                        file_path = os.path.join(path,img_dir,image)
                        with open(file_path,'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', '<{name}>'.format(name=image))
                            img.add_header('Content-Disposition', 'inline', filename=image)
                    except Exception as ex:
                        pass
                    email_msg = EmailMessage('Welcome to Eddi',email_html_template,email_from,recipient_list)
                    email_msg.content_subtype = 'html'
                    email_msg.attach(img)
                    try:
                        email_msg.attach(filename, pdf, "application/pdf")                         
                    except:
                        pass
                    email_msg.send(fail_silently=False)
                except Exception as ex:
                    pass
                return Response({MESSAGE: SUCCESS, DATA: {PAYMENT_INTENT:intent, EXTRA_MSG: extra_msg}}, status=status.HTTP_200_OK,)
            except Exception as ex:
                print(ex,"exex")
                return Response({MESSAGE: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)
        return Response({MESSAGE: 'Invalid Request', DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class Save_stripe_infoEvent(APIView):
    def post(self, request, *args, **kwargs):
            if request.method == POST_METHOD:
                user_email_id = request.POST.get(EMAIL_ID)
                amount = request.POST.get(PRICE)
                payment_method_id = request.POST.get(PAYMENT_METHOD_ID)
                event_name = request.POST.get(EVENT_NAME)
                extra_msg = ''
                # checking if customer with provided email already exists
                try:
                    var = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.get(**{EMAIL_ID:user_email_id, EVENT_NAME:event_name,STATUS:'Success'})
                    if var is not None:
                        return Response({MESSAGE: ERROR, DATA: "You already Enrolled"}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as ex:
                    pass
                
                try:
                    customer_data = stripe.Customer.list(email=user_email_id).data
                    if len(customer_data) == 0:
                        # creating customer
                        customer = stripe.Customer.create(email=user_email_id, payment_method=payment_method_id)
                    else:
                        customer = customer_data[0]
                        extra_msg = "Customer already existed."
                        
                    # creating paymentIntent
                    try:

                        intent = stripe.PaymentIntent.create(
                        amount=int(amount)*100,
                        currency='usd',
                        description='helllo',
                        customer=customer['id'],
                        payment_method_types=["card"],
                        payment_method=payment_method_id,
                        confirm=True)

                    except Exception as e:
                        return Response({MESSAGE: ERROR, DATA: "Error in stripe.PaymentIntent"}, status=status.HTTP_400_BAD_REQUEST)

                    try:
                        instance = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:user_email_id})
                        vat = getattr(models,"InvoiceVATCMS").objects.all().values_list("vat_value", flat=True)
                        vat_val = int(vat[0])
                        html_path = COURSE_ENROLL_HTML_TO_U
                        fullname = f'{instance.first_name} {instance.last_name}'
                        context_data = {'fullname':fullname, "course_name":event_name}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (instance.email_id,)
                        invoice_number = random.randrange(100000,999999)
                        context_data1 = {"invoice_number":invoice_number,"user_address":"User Address","issue_date":date.today(),"course_name":event_name,"course_fees": amount, "vat":vat_val, "total":int(amount) + (int(amount)*vat_val)/100}
                        template = get_template('invoice.html').render(context_data1)
                        try: 
                            result = BytesIO()
                            pdf = pisa.pisaDocument(BytesIO(template.encode("UTF-8")), result)#, link_callback=fetch_resources)
                            pdf = result.getvalue()
                            filename = f'Invoice-{invoice_number}.pdf'
                        except Exception as ex:
                            pass
                        record = {}
                        try:
                            record = {
                            "invoice_number" : invoice_number,
                            "user_address" : "Address",
                            "user_email" : instance.email_id,
                            "event_name" : event_name,
                            "vat_charges" : vat_val
                            }
                            getattr(models,"InvoiceDataEvent").objects.update_or_create(**record)
                        except Exception as ex:
                            pass
                        path = 'eddi_app'
                        img_dir = 'static'
                        image = 'Logo.jpg'
                        file_path = os.path.join(path,img_dir,image)
                        with open(file_path,'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', '<{name}>'.format(name=image))
                            img.add_header('Content-Disposition', 'inline', filename=image)
                        email_msg = EmailMessage('Welcome to Eddi',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        email_msg.attach(img)
                        try:
                            email_msg.attach(filename, pdf, "application/pdf")                         
                        except:
                            pass
                        email_msg.send(fail_silently=False)
                    except Exception as ex:
                        pass
                    return Response({MESSAGE: SUCCESS, DATA: {PAYMENT_INTENT:intent, EXTRA_MSG: extra_msg}}, status=status.HTTP_200_OK,)
                except Exception as ex:
                    return Response({MESSAGE: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)
            return Response({MESSAGE: 'Invalid Method Request', DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])   
class UserSignupView(APIView):
    def post(self, request):
        record_map = {}
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Method Not Allowed"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_type_id = getattr(models,USER_TYPE_TABLE).objects.only(ID).get(**{USER_TYPE:request.POST.get(USER_TYPE,None)})
        except:
            return Response({STATUS:ERROR, DATA: "Error Getting User Type"}, status=status.HTTP_400_BAD_REQUEST)
        
        record_map = {
            FIRST_NAME: request.POST.get(FIRST_NAME,None),
            LAST_NAME: request.POST.get(LAST_NAME,None),
            EMAIL_ID: request.POST.get(EMAIL_ID,None),            
            USER_TYPE_ID: user_type_id.id,
            STATUS_ID:1
        }
        try:
            if request.POST.get(PASSWORD):
                record_map[PASSWORD] = make_password(request.POST.get(PASSWORD))
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Need atleast password or is_login_from to login"}, status=status.HTTP_400_BAD_REQUEST)

        record_map[CREATED_AT] = make_aware(datetime.datetime.now())
        record_map[CREATED_BY] = 'admin'
        try:
            getattr(models,USERSIGNUP_TABLE).objects.update_or_create(**record_map)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "User Already Exists"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)


class GetUserDetails(APIView):
    def post(self, request):
        email_id =  get_user_email_by_token(request)
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.filter(**{'user_type__user_type':request.POST.get('user_type')})
            if serializer := UserSignupSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "No data found"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)


    def get(self, request,uuid = None):
        email_id =  get_user_email_by_token(request)
        if uuid:
            try:
                data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
                if getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == ADMIN_S:
                    if userSignup_serializer :=  UserSignupSerializer(data):
                    # Below Line : To make Active or Inactive to Particular user or supplier 
                        if data.user_type.user_type =='User':
                            try:
                                profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:data.email_id})
                            except Exception as ex:
                                return Response({STATUS: ERROR, DATA: "User profile data not data found"}, status=status.HTTP_400_BAD_REQUEST)

                            try:
                                course_enrolled = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{"email_id":data.email_id, "status":"Success"}).values_list("course_name", flat=True)
                                course_list = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"course_name__in":course_enrolled})
                            except Exception as ex:
                                return Response({STATUS: ERROR, DATA: "Error in User Course Listing"}, status=status.HTTP_400_BAD_REQUEST)
                                
                            if serializer := UserProfileSerializer(profile_data):
                                if serializer2 := CourseDetailsSerializer(course_list, many=True):
                                    return Response({STATUS: SUCCESS, DATA: [serializer.data,userSignup_serializer.data], "course_list":serializer2.data}, status=status.HTTP_200_OK)
                                else:
                                    return Response({STATUS: ERROR, DATA: serializer2.errors}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                        elif data.user_type.user_type ==SUPPLIER_S:
                            try:
                                supplier_course_count = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":data.email_id}).count()
                                supplier_all_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":data.email_id}).values_list("course_name", flat=True)
                                enrolled_count = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{"course_name__in":supplier_all_course, "status":"Success"}).count()
                                individuals_useremail = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{"course_name__in":supplier_all_course, "status":"Success"}).values_list("email_id", flat=True)
                                individuals_user = getattr(models,USER_PROFILE_TABLE).objects.filter(**{"email_id__in":individuals_useremail})
                            except Exception as ex:
                                return Response({STATUS: ERROR, DATA: "Error in filtering data"}, status=status.HTTP_400_BAD_REQUEST)

                            try:
                                try:
                                    organization_profile_data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:data.email_id})
                                except Exception as ex:
                                    organization_profile_data= None
                                try:
                                    supplier_profile_data = getattr(models,SUPPLIER_PROFILE_TABLE).objects.get(**{'supplier_email':data.email_id})
                                except Exception as ex:
                                    supplier_profile_data= None
                                if serializer := SupplierOrganizationProfileSerializer(organization_profile_data):
                                    if serializer1 := SupplierProfileSerializer(supplier_profile_data):
                                        if serializer2 := UserProfileSerializer(individuals_user, many=True):
                                            return Response({STATUS: SUCCESS, 'organization_profile': serializer.data, 'supplier_profile':[serializer1.data,userSignup_serializer.data], 'total_course':supplier_course_count, "learners":enrolled_count, "individual_list":serializer2.data}, status=status.HTTP_200_OK)
                                        else:
                                            return Response({STATUS: ERROR, DATA:serializer2.errors}, status=status.HTTP_400_BAD_REQUEST)
                                    else:
                                        return Response({STATUS: ERROR, DATA:serializer1.errors}, status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    return Response({STATUS: ERROR, DATA:serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                            except Exception as ex:
                                return Response({STATUS: ERROR, DATA:"Something went wrong in getting supplier profile"}, status=status.HTTP_400_BAD_REQUEST)
            
                        elif getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == SUPPLIER_S:  
                            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
                            if serializer := UserSignupSerializer(data):
                                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                            else:
                                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({STATUS: ERROR, DATA: serializer.errors, DATA:"Data not found in UserSignUp Table"}, status=status.HTTP_400_BAD_REQUEST)


                elif getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == SUPPLIER_S:
                    if userSignup_serializer :=  UserSignupSerializer(data):
                        if data.user_type.user_type =='User':
                            try:
                                profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:data.email_id})
                            except Exception as ex:
                                return Response({STATUS: ERROR, DATA: "User profile data not data found"}, status=status.HTTP_400_BAD_REQUEST)
                            try:
                                course_enrolled = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{"email_id":data.email_id, "status":"Success"}).values_list("course_name", flat=True)
                                course_list = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"course_name__in":course_enrolled})
                            except Exception as ex:
                                return Response({STATUS: ERROR, DATA: "Error in User Course Listing"}, status=status.HTTP_400_BAD_REQUEST)
                                
                            if serializer := UserProfileSerializer(profile_data):
                                if serializer2 := CourseDetailsSerializer(course_list, many=True):
                                    return Response({STATUS: SUCCESS, DATA: [serializer.data,userSignup_serializer.data], "course_list":serializer2.data}, status=status.HTTP_200_OK)
                                else:
                                    return Response({STATUS: ERROR, DATA: serializer2.errors}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                        
                        else:
                            return Response({STATUS: ERROR, DATA: "Requested UUID in not find in UserSignUPtable"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({STATUS: ERROR, DATA: serializer.errors, DATA:"Data not found in UserSignUp Table"}, status=status.HTTP_400_BAD_REQUEST)


            except Exception as ex:
                return Response({STATUS: ERROR, DATA:"Something went wrong in getting supplier profile or user profile"}, status=status.HTTP_400_BAD_REQUEST)
       
        else:
            data = getattr(models,USERSIGNUP_TABLE).objects.all()
            if serializer := UserSignupSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def put(self,request,uuid = None):
        email_id =  get_user_email_by_token(request)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Not Able to get user data"}, status=status.HTTP_400_BAD_REQUEST)
        record_map1 = {}
        if getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == ADMIN_S:
            if request.POST.get("status"):
                if request.POST.get("status") == "Active":
                    record_map1[STATUS_ID] = 1
                else:
                    record_map1[STATUS_ID] = 2
                for key,value in record_map1.items():
                    setattr(user_data,key,value)
                user_data.save() 
                return Response({STATUS: SUCCESS, DATA: "Data Successfully Edited"}, status=status.HTTP_200_OK)

        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            EMAIL_ID: data.email_id,
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
        email_id =  get_user_email_by_token(request)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "UUID not Provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            STATUS_ID:2,
            IS_DELETED :True
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = email_id
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data Succesfully Deleted"}, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class UserLoginView(APIView):
    def post(self, request):
        email_id = request.POST.get(EMAIL_ID)
        password = request.POST.get(PASSWORD)

        # Supplier Exception Case
        try:
            data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
        except Exception as ex:
            data= None
        if data is not None and str(data.is_approved.value) == "Rejected":
            return Response({STATUS: ERROR, DATA: "Your Profile is Rejected By Admin"}, status=status.HTTP_400_BAD_REQUEST)
        if data is not None and data.rejection_count == 3:
            return Response({STATUS: ERROR, DATA: "Your Profile Has Been Blocked. Please Contact Admin For Further Support"}, status=status.HTTP_400_BAD_REQUEST)
        if data is not None and str(data.is_approved.value) == "Pending":
            return Response({STATUS: ERROR, DATA: "Your Profile Is Under Review. You Can't Login Until It's Approved"}, status=status.HTTP_400_BAD_REQUEST)

        record_map = {}
        record_map = {
            FIRST_NAME: request.POST.get(FIRST_NAME,None),
            LAST_NAME: request.POST.get(LAST_NAME,None),
            EMAIL_ID: request.POST.get(EMAIL_ID,None),            
            IS_LOGIN_FROM : request.POST.get(IS_LOGIN_FROM,None),
            STATUS_ID:1
        }
        # User Social Login
        if request.POST.get("is_login_from"):
            if request.POST.get("is_login_from") != "normal":
                print("inside googlglgl")
                try:
                    d = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:request.POST.get(EMAIL_ID)})
                    if d.is_login_from == "google":
                        try:
                            user_profile = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                            if user_profile:
                                user_profile = True
                        except Exception as ex:
                            user_profile = False
                        token = NonBuiltInUserToken.objects.create(user_id = d.id)
                        return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:d.first_name, LAST_NAME:d.last_name} ,USER_TYPE:str(d.user_type),IS_FIRST_TIME_LOGIN: d.is_first_time_login,"is_resetpassword" : d.is_resetpassword,USER_PROFILE:user_profile,"Authorization":"Token "+ str(token.key)}, status=status.HTTP_200_OK)
                    else:
                        d.is_login_from = "google"
                        d.save()
                        return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:d.first_name, LAST_NAME:d.last_name} ,USER_TYPE:str(d.user_type),IS_FIRST_TIME_LOGIN: d.is_first_time_login,"is_resetpassword" : d.is_resetpassword,USER_PROFILE:user_profile,"Authorization":"Token "+ str(token.key)}, status=status.HTTP_200_OK)
                except Exception as ex:
                    record_map['USER_TYPE'] = "User"
                    getattr(models,USERSIGNUP_TABLE).objects.update_or_create(**record_map)
            
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id,IS_DELETED:False})
            token = NonBuiltInUserToken.objects.create(user_id = data.id)
        except Exception as ex:
            data = None
       
        try:
            user_profile = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
            if user_profile:
                user_profile = True
        except Exception as ex:
            user_profile = False

        # Supplier General Login
        try:
            if check_password(password, data.password) and data.user_type.user_type == SUPPLIER_S:
                return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:data.first_name, LAST_NAME:data.last_name} ,USER_TYPE:str(data.user_type),IS_FIRST_TIME_LOGIN: data.is_first_time_login,USER_PROFILE:user_profile,"is_resetpassword" : data.is_resetpassword,"Authorization":"Token "+ str(token.key),}, status=status.HTTP_200_OK)
        except Exception as ex:
            pass
        
        # General Admin Login
        try:
            if check_password(password, data.password) and data.user_type.user_type == ADMIN_S:
                return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:data.first_name, LAST_NAME:data.last_name} ,USER_TYPE:str(data.user_type),IS_FIRST_TIME_LOGIN: data.is_first_time_login,USER_PROFILE:user_profile,"is_resetpassword" : data.is_resetpassword,"Authorization":"Token "+ str(token.key),}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Your Activation Has Been Cancelled By The Admin"}, status=status.HTTP_400_BAD_REQUEST)

        # User Login Cases
        if data is not None:
            if data.status.id == 2:
                return Response({STATUS: ERROR, DATA: "Your Activation Has Been Cancelled By The Admin"}, status=status.HTTP_400_BAD_REQUEST)
            # if data.is_login_from == "google":
            #     return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:data.first_name, LAST_NAME:data.last_name} ,USER_TYPE:str(data.user_type),IS_FIRST_TIME_LOGIN: data.is_first_time_login,USER_PROFILE:user_profile,"Authorization":"Token "+ str(token.key)}, status=status.HTTP_200_OK)
            if not check_password(password, data.password):
                return Response({STATUS: ERROR, DATA: "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
            if data.is_active == True:
                return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:data.first_name, LAST_NAME:data.last_name} ,USER_TYPE:str(data.user_type),IS_FIRST_TIME_LOGIN: data.is_first_time_login,USER_PROFILE:user_profile,"is_resetpassword" : data.is_resetpassword,"Authorization":"Token "+ str(token.key),}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "User not Authorized"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({STATUS: ERROR, DATA: "User Not Found or User not Authenticated "}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class ForgetPasswordView(APIView):
    def post(self, request,uuid = None):
        email_id = request.POST.get(EMAIL_ID)
        request.session['forget-password'] = email_id
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id,STATUS_ID:1,IS_DELETED:False})
        except:
            data = None
        try:
            if data:
                if request.session.has_key('forget-password'):
                    html_path = RESETPASSWORD_HTML
                    fullname = data.first_name + " " + data.last_name
                    context_data = {"final_email": email_id,"fullname":fullname}
                    email_html_template = get_template(html_path).render(context_data)
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = (email_id,)
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
                    return Response({STATUS: SUCCESS, DATA: "Email Sent Successfully"}, status=status.HTTP_200_OK) 

            if data.user_type.user_type == SUPPLIER_S or data.user_type.user_type == ADMIN_S:
                html_path = RESETPASSWORDSupplierAdmin_HTML
                fullname = data.first_name + " " + data.last_name
                context_data = {"final_email": email_id,"fullname":fullname}
                email_html_template = get_template(html_path).render(context_data)
                email_from = settings.EMAIL_HOST_USER
                recipient_list = (email_id,)
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
                return Response({STATUS: SUCCESS, DATA: "Email Sent Successfully"}, status=status.HTTP_200_OK) 
            else:
                return Response({STATUS: ERROR, DATA: "You are not a registered user"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)
                

@permission_classes([AllowAny])
class ResetPasswordView(APIView):
    def post(self,request,slug=None):
        email_id = request.POST.get(EMAIL_ID)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id,STATUS_ID:1,IS_DELETED:False})
            password = request.POST.get(PASSWORD)
        except:
            data = None
        try:
            if data:
                setattr(data,PASSWORD,make_password(password))
                setattr(data,"is_resetpassword",False)
                setattr(data,MODIFIED_AT,make_aware(datetime.datetime.now()))
                setattr(data,MODIFIED_BY,'admin')
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Password Changed Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ex}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class VerifyUser(APIView):
    def get(self,request,uuid):
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
        except:
            data = None
            return Response({STATUS: ERROR, DATA: "UUID is not Valid"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if data:
                data.uuid = uuid4()
                data.is_active = True
                data.is_authenticated = True
                data.save()
                return Response({STATUS: SUCCESS, DATA: "User Verified Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "User not Verified"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
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
                setattr(data,IS_FIRST_TIME_LOGIN,False)

                setattr(data,MODIFIED_AT,make_aware(datetime.datetime.now()))
                setattr(data,MODIFIED_BY,'admin')
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Password Changed Successfull"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ex}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class Header_FooterCMSDetails(APIView):
   
    def get(self, request):
        try:
            try:
                data = getattr(models,HEADER_FOOTERCMS_TABLE).objects.latest(CREATED_AT)
            except Exception as ex:
                data = None
            if not (serializer := Header_FooterCMSSerializer(data)):
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class Header_FooterCMSDetails_sv(APIView):
    def get(self, request):
        try:
            try:
                data = getattr(models,"Header_FooterCMS_SV").objects.latest(CREATED_AT)
            except Exception as ex:
                data = None
            if not (serializer := Header_FooterCMSSerializer_sv(data)):
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class Testimonial(APIView):
    def get(self, request):
        try:
            data = getattr(models,"TestinomialsDetails").objects.all().values_list("id", flat=True)
            l = list(data)
            shuffle(l)
            data1 = getattr(models,"TestinomialsDetails").objects.filter(**{"pk__in":l[:3]})
            if serializer := TestinomialsDetailsSerializer(data1, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA:serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class Testimonial_sv(APIView):
    def get(self, request):
        try:
            data = getattr(models,"TestinomialsDetails_SV").objects.all().values_list("id", flat=True)
            l = list(data)
            shuffle(l)
            data1 = getattr(models,"TestinomialsDetails_SV").objects.filter(**{"pk__in":l[:3]})
            if serializer := TestinomialsDetailsSerializer_sv(data1, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA:serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class GetHomePageDetails(APIView):
    def get(self, request):
        try:
            data = getattr(models,HOMEPAGECMS_TABLE).objects.latest(CREATED_AT)
            event_data = EventAd.objects.filter(Q(event_publish_on="Landing Page") | Q(event_publish_on="Both"))
            if not (serializer := HomePageCMSSerializer(data)):
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            elif not (event_serializer := EventAdSerializer(event_data, many=True)):
                return Response({STATUS: ERROR, DATA: event_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({STATUS: SUCCESS, DATA: serializer.data, EVENT_DATA:event_serializer.data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class GetHomePageDetails_sv(APIView):
    def get(self, request):
        try:
            try:
                data = getattr(models,"HomePageCMS_SV").objects.latest(CREATED_AT)
            except Exception as ex:
                data = None
            event_data = EventAd.objects.filter(Q(event_publish_on="Landing Page") | Q(event_publish_on="Both"))
            if not (serializer := HomePageCMSSerializer_sv(data)):
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            elif not (event_serializer := EventAdSerializer(event_data, many=True)):
                return Response({STATUS: ERROR, DATA: event_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({STATUS: SUCCESS, DATA: serializer.data, EVENT_DATA:event_serializer.data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class GetPrivacyPolicyDetails(APIView): 
    def get(self, request):
        data = getattr(models,PRIVACY_POLICY_CMS_TABLE).objects.latest(CREATED_AT)
        if not (serializer := PrivacyPolicyPageCMSSerializer(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class GetPrivacyPolicyDetails_sv(APIView): 
    def get(self, request):
        try:
            data = getattr(models,"PrivacyPolicyCMS_SV").objects.latest(CREATED_AT)
        except Exception as ex:
            data = None
        if not (serializer := PrivacyPolicyPageCMSSerializer_sv(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class GetPrivacyPolicySupplierDetails(APIView): 
    def get(self, request):
        data = getattr(models,PRIVACY_POLICY_CMS_SUPPLIER_TABLE).objects.latest(CREATED_AT)
        if not (serializer := PrivacyPolicySupplierPageCMSSerializer(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class GetPrivacyPolicySupplierDetails_sv(APIView): 
    def get(self, request):
        try:
            data = getattr(models,"PrivacyPolicyCMSSupplier_SV").objects.latest(CREATED_AT)
        except Exception as ex:
            data = None
        if not (serializer := PrivacyPolicySupplierPageCMSSerializer_sv(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class GetTermsConditionDetails(APIView): 
    def get(self, request):
        data = getattr(models,TERMS_CONDITION_CMS_TABLE).objects.latest(CREATED_AT)
        if not (serializer := TermsConditionPageCMSSerializer(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class GetTermsConditionDetails_sv(APIView): 
    def get(self, request):
        try:
            data = getattr(models,"TermsConditionCMS_SV").objects.latest(CREATED_AT)
        except Exception as ex:
            data = None
        if not (serializer := TermsConditionPageCMSSerializer_sv(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class GetTermsConditionSupplierDetails(APIView): 
    def get(self, request):
        data = getattr(models,TERMS_CONDITION_CMS_SUPPLIER_TABLE).objects.latest(CREATED_AT)
        if not (serializer := TermsConditionSupplierPageCMSSerializer(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class GetTermsConditionSupplierDetails_sv(APIView): 
    def get(self, request):
        try:
            data = getattr(models,"TermsConditionCMSSupplier_SV").objects.latest(CREATED_AT)
        except Exception as ex:
            data = None
        if not (serializer := TermsConditionSupplierPageCMSSerializer(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])   
class GetAboutUsPageDetails(APIView):
    def get(self, request):
            data = getattr(models,ABOUTUSCMS_TABLE).objects.latest(CREATED_AT)
            if serializer := AboutUsCMSSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])   
class GetAboutUsPageDetails_sv(APIView):
    def get(self, request):
        try:
            try:
                data = getattr(models,"AboutUsPageCMS_SV").objects.latest(CREATED_AT)
            except Exception as ex:
                data = None
            if serializer := AboutUsCMSSerializer_sv(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            print(ex,"exexe")

@permission_classes([AllowAny])
class GetContactUsPageDetails(APIView):
    def get(self, request):
            data = getattr(models,CONTACTUSCMS_TABLE).objects.latest(CREATED_AT)
            if serializer := ContactUsCMSSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class GetContactUsPageDetails_sv(APIView):
    def get(self, request):
            try:
                data = getattr(models,"ContactUsPageCMS_SV").objects.latest(CREATED_AT)
            except Exception as ex:
                data = None    
            if serializer := ContactUsCMSSerializer_sv(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
@permission_classes([AllowAny])
class GetBlogDetails(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,BLOGDETAILS_TABLE).objects.get(**{UUID:uuid})
            try:
                related_blog = list(getattr(models,BLOGDETAILS_TABLE).objects.filter(**{BLOG_CATEGORY_ID:data.blog_category.id}).order_by('-created_date_time').exclude(id = data.id).values())
                for i in related_blog:
                    for key,value in i.items():
                        if key == 'blog_image':
                            i[key] = "/media/" + value
            except:
                related_blog = []
            
            if serializer := BlogDetailsSerializer(data):
                
                return Response({STATUS: SUCCESS, DATA: serializer.data, RELATED_BLOG:related_blog}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            
            data = getattr(models,BLOGDETAILS_TABLE).objects.all().order_by("-created_date_time")
            if serializer := BlogDetailsSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class GetBlogDetails_sv(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,"BlogDetails_SV").objects.get(**{UUID:uuid})
            try:
                related_blog = list(getattr(models,"BlogDetails_SV").objects.filter(**{BLOG_CATEGORY_ID:data.blog_category.id}).order_by('-created_date_time').exclude(id = data.id).values())
                for i in related_blog:
                    for key,value in i.items():
                        if key == 'blog_image':
                            i[key] = "/media/" + value
            except:
                related_blog = []
            
            if serializer := BlogDetailsSerializer_sv(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data, RELATED_BLOG:related_blog}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            
            data = getattr(models,BLOGDETAILS_TABLE).objects.all().order_by("-created_date_time")
            if serializer := BlogDetailsSerializer_sv(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
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
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    def post(self, request):
        email_id = get_user_email_by_token(request)
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
        except Exception as ex:
            data= None
        if serializer := UserProfileSerializer(data):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Not Able to get userprofile data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {
            PROFILE_IMAGE : request.FILES.get(PROFILE_IMAGE,data.profile_image),
            FIRST_NAME : request.POST.get(FIRST_NAME,data.first_name),
            LAST_NAME : request.POST.get(LAST_NAME,data.last_name),
            GENDER : request.POST.get(GENDER,data.gender),
            DOB : request.POST.get(DOB,data.dob),
            PERSONAL_NUMBER : request.POST.get(PERSONAL_NUMBER,data.personal_number),
            PHONE_NUMBER : request.POST.get(PHONE_NUMBER,data.phone_number),
            LOCATION : request.POST.get(USER_LOCATION,None),
            USER_INTERESTS : request.POST.get(USER_INTERESTS,None),
            HIGHEST_EDUCATION : request.POST.get(HIGHEST_EDUCATION,data.highest_education),
            UNIVERSITY_NAME : request.POST.get(UNIVERSITY_NAME,data.university_name),
            HIGHEST_DEGREE : request.POST.get(HIGHEST_DEGREE,data.highest_degree),
            EDUCATIONAL_AREA : request.POST.get(EDUCATIONAL_AREA,data.educational_area),
            OTHER_EDUCATION : request.POST.get(OTHER_EDUCATION,data.other_education),
            DIPLOMAS_CERTIFICATES : request.POST.get(DIPLOMAS_CERTIFICATES,data.diplomas_certificates),
            CURRENT_PROFESSIONAL_ROLE : request.POST.get(CURRENT_PROFESSIONAL_ROLE,data.current_professional_role),
            ADDITIONAL_ROLE : request.POST.get(ADDITIONAL_ROLE,data.additional_role),
            EXTRA_CURRICULAR : request.POST.get(EXTRA_CURRICULAR,data.extra_curricular),
            EXTRA_CURRICULAR_COMPETENCE : request.POST.get(EXTRA_CURRICULAR_COMPETENCE,data.extra_curricular_competence),
            CORE_RESPONSIBILITIES : request.POST.get(CORE_RESPONSIBILITIES,data.core_responsibilities),
            LEVEL_OF_ROLE : request.POST.get(LEVEL_OF_ROLE,data.level_of_role),
            FUTURE_PROFESSIONAL_ROLE : request.POST.get(FUTURE_PROFESSIONAL_ROLE,data.future_professional_role),
            COURSE_CATEGORY : request.POST.get(COURSE_CATEGORY,data.course_category),            
            AREA_OF_INTEREST : request.POST.get(AREA_OF_INTEREST,data.area_of_interest),            
        }
            if request.POST.get(AGREE_ADS_TERMS):
                record_map[AGREE_ADS_TERMS] = json.loads(request.POST.get(AGREE_ADS_TERMS))
            else:
                record_map[AGREE_ADS_TERMS] = data.agree_ads_terms
            if request.POST.get(PASSWORD):
                var = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
                recordd = {}
                recordd = {
                    PASSWORD: make_password(request.POST.get(PASSWORD))
                }
                for key,value in recordd.items():
                    setattr(var,key,value)
                var.save()    

            record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()            
            return Response({STATUS: SUCCESS, DATA: "Profile Updated Successfully"}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in saving Edited data"}, status=status.HTTP_400_BAD_REQUEST)
            
            
@permission_classes([AllowAny])
class UserPaymentDetail_info(APIView):
    def post(self, request):
        try:
            course_name = request.POST.get(COURSE_NAME)
            email_id = request.POST.get(EMAIL_ID)
            user_type = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type
            if request.POST.get(CARD_BRAND):
                card_type = request.POST.get(CARD_BRAND)
            else:
                card_type = None
            if request.POST.get(PRICE):
                amount = request.POST.get(PRICE)
            else:
                amount = 0
            if request.POST.get(STATUS):
                status_s = request.POST.get(STATUS)
            else:
                status_s = "Success"           
            record_map = {}
            record_map = {
                COURSE_NAME : course_name,
                EMAIL_ID: email_id,
                CARD_TYPE : card_type,
                AMOUNT: float(amount),
                STATUS: status_s,
                CREATED_AT : make_aware(datetime.datetime.now())
                }
            try:
                var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, COURSE_NAME:course_name,STATUS:'Success'})
            except Exception as ex:
                var = None
            if not var:
                try:
                    getattr(models,USER_PAYMENT_DETAIL).objects.update_or_create(**record_map)
                    profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:request.POST.get(EMAIL_ID)})
                    var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, COURSE_NAME:course_name,STATUS:'Success'})
                    courseobj = getattr(models,COURSEDETAILS_TABLE).objects.get(**{COURSE_NAME:course_name})
                    record_map = {}
                    record_map = {
                    COURSE_CATEGORY : courseobj.course_category,
                    SUPPLIER_EMAIL : courseobj.supplier.email_id,
                    PAYMENT_DETAIL_ID : var.id,
                    USER_PROFILE_ID : profile_data.id,
                    CREATED_AT : make_aware(datetime.datetime.now())
                    }
                    getattr(models,COURSE_ENROLL_TABLE).objects.update_or_create(**record_map)
                    try:
                        supplier_data = getattr(models,SupplierOrganizationProfile).objects.get(**{"supplier_email":courseobj.supplier.email_id})
                    except Exception as ex:
                        pass
                    try:
                        sender_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{"email_id":email_id})
                    except Exception as ex:
                        pass
                    try:
                        message = f"{sender_data.first_name}, has applied for {courseobj.course_name}"
                        send_notification(email_id, courseobj.supplier.email_id, message)
                    except Exception as ex:
                        pass
                    return Response({STATUS: SUCCESS, DATA: "Created Successfully"}, status=status.HTTP_200_OK)

                except Exception as ex:
                    return Response({MESSAGE: ERROR, DATA: "Data Creation Error"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({MESSAGE: ERROR, DATA: "You Already Enrolled"}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as ex:
            return Response({STATUS:ERROR, DATA:"ERROR"}, status=status.HTTP_400_BAD_REQUEST)
                

@permission_classes([AllowAny])
class EventPaymentDetail_info(APIView):
    def post(self, request):
        user_email_id = get_user_email_by_token(request)
        try:
            event_name = request.POST.get(EVENT_NAME)
            if request.POST.get(CARD_BRAND):
                card_type = request.POST.get(CARD_BRAND)
            else:
                card_type = None
            if request.POST.get(PRICE):
                amount = request.POST.get(PRICE)
            else:
                amount = 0
            if request.POST.get(STATUS):
                status_s = request.POST.get(STATUS)
            else:
                status_s = "Success"
                           
            record_map = {}
            record_map = {
                EVENT_NAME : event_name,
                EMAIL_ID: user_email_id,
                CARD_TYPE : card_type,
                AMOUNT: float(amount),
                STATUS: status_s,
                CREATED_AT : make_aware(datetime.datetime.now())
                }
            try:
                var = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.get(**{EMAIL_ID:user_email_id, EVENT_NAME:event_name,STATUS:'Success'})
            except Exception as ex:
                var = None
            if not var:
                try:
                    getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.update_or_create(**record_map)
                    profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:user_email_id})
                    var = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.get(**{EMAIL_ID:user_email_id, EVENT_NAME:event_name,STATUS:'Success'})
                    record_map = {}
                    record_map = {
                    EVENT_NAME : event_name,
                    USER_EMAIL : user_email_id,
                    PAYMENT_DETAIL_ID : var.id,
                    USER_PROFILE_ID : profile_data.id,
                    CREATED_AT : make_aware(datetime.datetime.now())
                    }
                    getattr(models,EVENTAD_ENROLL_TABLE).objects.update_or_create(**record_map)
                    
                    return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)

                except Exception as ex:
                    return Response({MESSAGE: ERROR, DATA: "Data Creation Error"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({MESSAGE: ERROR, DATA: "You Already Enrolled"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS:ERROR, DATA:ERROR}, status=status.HTTP_400_BAD_REQUEST)


class FavCourseDetails(APIView):
    def post(self, request):
        data = None
        email_id = None
        user_data_fav = None
        is_favourite_data = None
        record_map = {}
        email_id = get_user_email_by_token(request)
        
        try:
            course_name = request.POST.get(COURSE_NAME)
            user_data_fav = getattr(models,FAVOURITE_COURSE_TABLE).objects.filter(**{COURSE_NAME:course_name}).get(**{EMAIL_ID:email_id}).order_by('-created_date_time')
        except Exception as ex:
            user_data_fav = None
            
        if user_data_fav:
            fav_data = request.POST.get(IS_FAVOURITE)
            
            if fav_data == 'true':
                setattr(user_data_fav,IS_FAVOURITE,True)
                user_data_fav.save()
            else:
                setattr(user_data_fav,IS_FAVOURITE,False)
                user_data_fav.save()
        else:
            course_name = request.POST.get(COURSE_NAME)
            fav_data = request.POST.get(IS_FAVOURITE)
            
            if fav_data == 'true':
                is_favourite_data = True
            else:
                is_favourite_data = False
                
            record_map = {
                EMAIL_ID: email_id,
                COURSE_NAME : course_name,
                IS_FAVOURITE: is_favourite_data,
                CREATED_AT : make_aware(datetime.datetime.now())
                }
            try:
                getattr(models,FAVOURITE_COURSE_TABLE).objects.update_or_create(**record_map)
                return Response({MESSAGE: SUCCESS, DATA: "Created"}, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({MESSAGE: ERROR, DATA: "ERROR creating data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({MESSAGE: SUCCESS, DATA: "Done"}, status=status.HTTP_200_OK)
            
    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            if getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type =='User':
                try:
                    data = getattr(models,FAVOURITE_COURSE_TABLE).objects.filter(**{EMAIL_ID:email_id, 'is_favourite':True}).values_list("course_name", flat = True).order_by("-created_date_time")
                except Exception as ex:
                    data= None
                try:
                    course_data = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{'course_name__in':list(data)})
                except:
                    course_data = None

                if serializer := CourseDetailsSerializer(course_data, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 
        except:
            return Response({STATUS: ERROR, DATA: "Error getting favourite course data"}, status=status.HTTP_400_BAD_REQUEST)


class ViewIndividualProfile(APIView):
    def post(self, request):
        email_id = get_user_email_by_token(request)
        user_email_id = request.POST.get(EMAIL_ID)
        supplier_email_id = request.POST.get(SUPPLIER_EMAIL_ID)
        token_data = request.headers.get('Authorization')
        try:
            token = token_data.split()[1]   
            data = getattr(models,TOKEN_TABLE).objects.get(key = token)
        except Exception as ex:
            return Response({MESSAGE: "Error", DATA: "Token Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course_list = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__email_id":user_email_id, SUPPLIER_EMAIL:supplier_email_id})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Course list Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:user_email_id})          
            if serializer := UserProfileSerializer(profile_data):
                if serializer1 := CourseEnrollSerializer(course_list, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data, "Course":serializer1.data, "Ongoing_Course":course_list.count()}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: "Serializing CourseEnrolled data Error"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({STATUS: ERROR, DATA: "Serializing userprofile data Error"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class IncreaseAdCount(APIView):
    def put(self, request, uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "not get uuid"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,EVENT_AD_TABLE).objects.get(**{UUID:uuid})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        if data.event_subscriber == None:
            data.event_subscriber = 1
        else:
            data.event_subscriber += 1
        record_map = {
            EVENT_SUBSCRIBER : data.event_subscriber,
        }
        for key,value in record_map.items():
                setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)

class IncreaserecruitmentAdCount(APIView):
    def put(self, request, uuid = None):
        email_id = get_user_email_by_token(request)
        try:
            user_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Can't get User Profile with given email"}, status=status.HTTP_400_BAD_REQUEST)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "not get uuid"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,"RecruitmentAd").objects.get(**{UUID:uuid})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Not Able to get data from RecruitmentAd Table"}, status=status.HTTP_400_BAD_REQUEST)
        data_user = getattr(models,"RecruitmentAd").objects.get(**{UUID:uuid})    
        user_list = data_user.user_profile.all().values_list("email_id", flat=True)
        if user_data.email_id not in user_list:
            data_user.user_profile.add(user_data.id)
            if data.subscriber_count == None:
                data.subscriber_count = 1
            else:
                data.subscriber_count += 1
        
        record_map = {
            "subscriber_count" : data.subscriber_count,
            UUID : uuid4()
        }
        for key,value in record_map.items():
                setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Subscriber Count Increased Successfully"}, status=status.HTTP_200_OK)
        

class EventView(APIView):
    def post(self, request):
        record_map = {}
        try:
            record_map = {
            EVENT_IMAGE : request.FILES.get(EVENT_IMAGE,None),
            EVENT_PUBLISH_ON : request.POST.get(EVENT_PUBLISH_ON,None),
            EVENT_NAME : request.POST.get(EVENT_NAME,None),
            EVENT_CATEGORY : request.POST.get(EVENT_CATEGORY,None),
            EVENT_CHOOSE_TYPE : request.POST.get(EVENT_CHOOSE_TYPE,None),
            BANNER_VIDEO_LINK : request.POST.get(BANNER_VIDEO_LINK,None),
            FEES_TYPE : request.POST.get(FEES_TYPE,None),
            EVENT_TYPE : request.POST.get(EVENT_TYPE,None),
            EVENT_PRICE : request.POST.get(EVENT_PRICE,None),
            CHECKOUT_LINK : request.POST.get(CHECKOUT_LINK,None),
            MEETING_LINK : request.POST.get(MEETING_LINK,None),
            MEETING_PASSCODE : request.POST.get(MEETING_PASSCODE,None),
            EVENT_SMALL_DESCRIPTION : request.POST.get(EVENT_SMALL_DESCRIPTION,None),
            EVENT_DESCRIPTION : request.POST.get(EVENT_DESCRIPTION,None),
            EVENT_LOCATION: request.POST.get(EVENT_LOCATION,None),
            EVENT_ORGANIZER : request.POST.get(EVENT_ORGANIZER,None),
            EVENT_SUBSCRIBER : request.POST.get(EVENT_SUBSCRIBER,None),
            STATUS_ID:1
           
        }
            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[UUID] = uuid4()
            if request.POST.get(START_DATE) == "":
                record_map[START_DATE] = None
            else:
                record_map[START_DATE] = request.POST.get(START_DATE)

            if request.POST.get(START_TIME) == "":
                record_map[START_TIME] = None
            else:
                record_map[START_TIME] = request.POST.get(START_TIME)

            if request.POST.get(IS_FEATURED) == "true":
                featured_data = True
            else:
                featured_data = False
            record_map[IS_FEATURED] = featured_data
            getattr(models,EVENT_AD_TABLE).objects.update_or_create(**record_map)
            return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, uuid = None):
        email_id = get_user_email_by_token(request)
        try:
            vat = getattr(models,"InvoiceVATCMS").objects.all().values_list("vat_value", flat=True)
            vat_val = int(vat[0])
        except Exception as ex:
            vat_val = None
        if uuid:
            data = getattr(models,EVENT_AD_TABLE).objects.get(**{UUID:uuid})
            individuals = getattr(models,EVENTAD_ENROLL_TABLE).objects.filter(**{EVENT_NAME:data.event_name})
            subscriber = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.filter(**{EVENT_NAME:data.event_name, "status":"Success"}).count()
            try:
                var = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.get(**{EMAIL_ID:email_id, EVENT_NAME:data.event_name,STATUS:'Success'})
            except Exception as ex:
                var = None
            var1 = True if var is not None else False
           
            if serializer := EventAdSerializer(data):
                if serializer2 := EventAdEnrollSerializer(individuals, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data, SUBSCRIBER_COUNT:subscriber, "is_enrolled":var1, "VAT_charges":vat_val, "individuals":serializer2.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer2.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == ADMIN_S:
                try:
                    data_a = getattr(models,EVENT_AD_TABLE).objects.all().order_by("-created_date_time")
                except Exception as ex:
                    return Response({STATUS: ERROR, DATA:ERROR }, status=status.HTTP_400_BAD_REQUEST)
                if serializer := EventAdSerializer(data_a,many=True):
                        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                try:
                    cat = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                    a = cat.course_category.split(",")
                except Exception as ex:
                    a = cat.course_category.split()
                user_data = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.filter(**{EMAIL_ID:email_id}).values_list("event_name", flat=True)
                category_event = getattr(models,EVENT_AD_TABLE).objects.filter(**{STATUS_ID:1,IS_DELETED:False}).filter(Q(event_name__in = a) | Q(event_category__in = a)).exclude(event_name__in = user_data).order_by("-created_date_time")

                category_event_data = getattr(models,EVENT_AD_TABLE).objects.filter(**{STATUS_ID:1,IS_DELETED:False}).filter(Q(event_name__in = a) | Q(event_category__in = a)).exclude(event_name__in = user_data).values_list(EVENT_NAME, flat=True)

                all_event_data = getattr(models,EVENT_AD_TABLE).objects.filter(**{STATUS_ID:1,IS_DELETED:False}).exclude(event_name__in = category_event_data).order_by("-created_date_time")

                if serializer := EventAdSerializer(category_event, many=True):
                    if serializer1 := EventAdSerializer(all_event_data, many=True):
                        return Response({STATUS: SUCCESS, DATA: serializer.data, "all_event":serializer1.data}, status=status.HTTP_200_OK)
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self, request, uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,EVENT_AD_TABLE).objects.get(**{UUID:uuid})            
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            enrolled = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.filter(**{EVENT_NAME:data.event_name})
            if enrolled.exists():
                return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Event You Can't Edit"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            pass
        
        try:
            record_map = {
            EVENT_IMAGE : request.FILES.get(EVENT_IMAGE,data.event_image),
            EVENT_PUBLISH_ON : request.POST.get(EVENT_PUBLISH_ON,data.event_publish_on),
            EVENT_NAME : request.POST.get(EVENT_NAME,data.event_name),
            EVENT_CHOOSE_TYPE : request.POST.get(EVENT_CHOOSE_TYPE,data.event_choose_type),
            EVENT_CATEGORY : request.POST.get(EVENT_CATEGORY,data.event_category),
            BANNER_VIDEO_LINK : request.POST.get(BANNER_VIDEO_LINK,data.banner_video_link),  
            FEES_TYPE : request.POST.get(FEES_TYPE,data.fees_type),
            EVENT_TYPE : request.POST.get(EVENT_TYPE,data.event_type),
            EVENT_PRICE : request.POST.get(EVENT_PRICE,data.event_price),
            CHECKOUT_LINK : request.POST.get(CHECKOUT_LINK,data.checkout_link),
            MEETING_LINK : request.POST.get(MEETING_LINK,data.meeting_link),
            MEETING_PASSCODE : request.POST.get(MEETING_PASSCODE,data.meeting_passcode),
            EVENT_SMALL_DESCRIPTION : request.POST.get(EVENT_SMALL_DESCRIPTION,data.event_small_description),
            EVENT_DESCRIPTION : request.POST.get(EVENT_DESCRIPTION,data.event_description),
            EVENT_LOCATION: request.POST.get(EVENT_LOCATION,data.event_location),
            EVENT_ORGANIZER : request.POST.get(EVENT_ORGANIZER,data.event_organizer),
            EVENT_SUBSCRIBER : request.POST.get(EVENT_SUBSCRIBER,data.event_subscriber),
            
            }
        
            if request.POST.get(START_DATE) == "":
                record_map[START_DATE] = None
            else:
                record_map[START_DATE] = request.POST.get(START_DATE, data.start_date)

            if request.POST.get(START_TIME) == "":
                record_map[START_TIME] = None
            else:
                record_map[START_TIME] = request.POST.get(START_TIME, data.start_time)

            if request.POST.get(STATUS):
                if request.POST.get(STATUS) == "Active":
                    record_map[STATUS_ID] = 1
                else:
                    try:
                        dataa = getattr(models,EVENTAD_ENROLL_TABLE).objects.filter(**{EVENT_NAME:data.event_name})
                    except Exception as ex:
                        dataa = None
                    if dataa.exists():
                        return Response({STATUS: ERROR, DATA: "Someone Already Enrolled in This Event"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        record_map[STATUS_ID] = 2
            else:
                record_map[STATUS_ID] = data.status
            record_map[UUID] = uuid4()
            if request.POST.get(IS_FEATURED) == "true":
                featured_data = True
            else:
                featured_data = False
            record_map[IS_FEATURED] = featured_data
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()
            return Response({STATUS: SUCCESS, DATA: "Edited Successfully"}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self,request,uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,EVENT_AD_TABLE).objects.get(**{UUID:uuid})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {}
            record_map[STATUS_ID] = 2
            record_map[IS_DELETED] = True
            record_map[UUID] = uuid4()
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()
            return Response({STATUS: SUCCESS, DATA: "Data Succesfully Deleted"}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in Deleting Data"}, status=status.HTTP_200_OK)


class RecruitmentAdView(APIView):
    def post(self, request):
        email_id =  get_user_email_by_token(request)
        record_map = {}
        try:
            supplier_id = getattr(models,"SupplierProfile").objects.get(**{"supplier_email":email_id})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Need to Add Supplier Profile First"}, status=status.HTTP_200_OK)
        try:
            record_map = {
            RECRUITMENTAD_FILE : request.FILES.get(RECRUITMENTAD_FILE,None),
            RECRUITMENTAD_TITLE : request.POST.get(RECRUITMENTAD_TITLE,None),
            RECRUITMENTAD_DESCRIPTION : request.POST.get(RECRUITMENTAD_DESCRIPTION,None),
            SUPPLIER_PROFILE : supplier_id,
            RECRUITMENTAD_BANNER_VIEDO_LINK : request.POST.get(RECRUITMENTAD_BANNER_VIEDO_LINK,None),
            RECRUITMENTAD_EXPIRY : request.POST.get(RECRUITMENTAD_EXPIRY,None),
            STATUS_ID:1,
            IS_APPROVED_ID : 2
            }

            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[CREATED_BY] = email_id
            record_map[UUID] = uuid4()
            
            getattr(models,RECRUITMENTAD_TABLE).objects.update_or_create(**record_map)
            return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in saving data"}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, uuid = None):
        email_id =  get_user_email_by_token(request)
        if uuid:
            data = getattr(models,RECRUITMENTAD_TABLE).objects.get(**{UUID:uuid})
            if serializer := RecruitmentAdSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == "User" and getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id}).agree_ads_terms == True:
                data = getattr(models,RECRUITMENTAD_TABLE).objects.filter(**{"recruitmentAd_Expiry__gte":datetime.datetime.now().date()}).order_by("-created_date_time")
                if serializer := RecruitmentAdSerializer(data, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            elif getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == ADMIN_S:
                data = getattr(models,RECRUITMENTAD_TABLE).objects.all().order_by("-created_date_time")
                if serializer := RecruitmentAdSerializer(data, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            elif getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == SUPPLIER_S:
                try:
                    data = getattr(models,RECRUITMENTAD_TABLE).objects.filter(**{"supplier_profile__supplier_email":email_id}).order_by("-created_date_time")
                except Exception as ex:
                    return Response({STATUS: ERROR, DATA: "You have not added Recruitment Ads Yet"}, status=status.HTTP_400_BAD_REQUEST)
                if serializer := RecruitmentAdSerializer(data, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({STATUS: ERROR, DATA: "You have not Agreed to get Recruitment Ads"}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, uuid = None):
        email_id =  get_user_email_by_token(request)
        try:
            user_type_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type
        except Exception:
            user_type_data = None
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,RECRUITMENTAD_TABLE).objects.get(**{UUID:uuid})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            record_map = {
            RECRUITMENTAD_FILE : request.FILES.get(RECRUITMENTAD_FILE,data.recruitmentAd_File),
            RECRUITMENTAD_TITLE : request.POST.get(RECRUITMENTAD_TITLE,data.recruitmentAd_title),
            RECRUITMENTAD_DESCRIPTION : request.POST.get(RECRUITMENTAD_DESCRIPTION,data.recruitmentAd_description),
            RECRUITMENTAD_BANNER_VIEDO_LINK : request.POST.get(RECRUITMENTAD_BANNER_VIEDO_LINK,data.recruitmentAd_banner_video_link),
            RECRUITMENTAD_EXPIRY : request.POST.get(RECRUITMENTAD_EXPIRY,data.recruitmentAd_Expiry),
            }

            if user_type_data:
                if user_type_data == ADMIN_S:
                    if request.POST.get(STATUS):
                        if request.POST.get(STATUS) == "Active":
                            record_map[STATUS_ID] = 1
                        else:
                            record_map[STATUS_ID] = 2
                    else:
                        record_map[STATUS] = data.status

                    if request.POST.get(APPROVAL_STATUS):
                        if request.POST.get(APPROVAL_STATUS) == "Approved":
                            record_map[IS_APPROVED_ID] = 1
                        elif request.POST.get(APPROVAL_STATUS) == "Pending":
                            record_map[IS_APPROVED_ID] = 2
                        else:
                            record_map[IS_APPROVED_ID] = 3
                    else:
                        record_map[IS_APPROVED] = data.is_approved

                elif user_type_data == SUPPLIER_S:
                    if request.POST.get(STATUS):
                        if request.POST.get(STATUS) == "Active":
                            record_map[STATUS_ID] = 1
                        else:
                            record_map[STATUS_ID] = 2
                    else:
                        record_map[STATUS] = data.status
                        record_map[IS_APPROVED_ID] = 2

            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[UUID] = uuid4()
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()            
            return Response({STATUS: SUCCESS, DATA: "Edited Data successfully"}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in saving data"}, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self,request,uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,RECRUITMENTAD_TABLE).objects.get(**{UUID:uuid})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {}
            record_map[STATUS_ID] = 2
            record_map[IS_DELETED] = True
            record_map[UUID] = uuid4()
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()
            return Response({STATUS: SUCCESS, DATA: "Data Succesfully Deleted"}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in Deleting Data"}, status=status.HTTP_200_OK)



# For My Course Page
class CourseEnrollView(APIView):
    def post(self, request):
        email_id =  get_user_email_by_token(request)
        var = request.POST.get("filter")
        try:
            enroll_data = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{'user_profile__email_id':email_id}).values_list("payment_detail__course_name", flat = True)
        except Exception as ex:
            enroll_data = None
        try:
            course_data = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{'course_name__in':list(enroll_data)}).order_by("-created_date_time")
        except:
            course_data = None

        try:
            course_data_uuid = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{'course_name__in':list(enroll_data)}).values_list('uuid', flat=True).order_by("-created_date_time")
            
        except Exception as ex:
            course_data_uuid = None

        if var == "all":
            new_dict = OrderedDict()
            try:
                for i in list(course_data_uuid): 
                    try:
                        var = getattr(models,"CourseMaterial").objects.get(**{'course__uuid':i})
                        all_videos = var.video_files.all()
                    except Exception as ex:
                            var = None
                            new_dict[f"course_{i}"] = "Ongoing"
                            continue
                    l1 = []
                    for j in all_videos:
                        try:
                            material_status = getattr(models,"CourseMaterialStatus").objects.get(**{'user_email':email_id, 'video_id':j.uuid})
                            l1.append(material_status.is_complete)
                        except Exception as ex:
                            pass
                    if len(l1) != len(all_videos) or False in l1:
                        new_dict[f"course_{i}"] = "Ongoing"
                    else:
                        new_dict[f"course_{i}"] = "Completed"                          

            except Exception as ex:
                pass

        elif var == "ongoing":
            new_dict = OrderedDict()
            try:
                ongoing_coures_uuid = []
                for i in list(course_data_uuid): 
                    try:
                        var = getattr(models,"CourseMaterial").objects.get(**{'course__uuid':i})
                        all_videos = var.video_files.all()
                    except Exception as ex:
                        var = None
                        new_dict[f"course_{i}"] = "Ongoing"
                        ongoing_coures_uuid.append(i)
                        continue
                    l1 = []
                    for j in all_videos:
                        try:
                            material_status = getattr(models,"CourseMaterialStatus").objects.get(**{'user_email':email_id, 'video_id':j.uuid})
                            l1.append(material_status.is_complete)
                        except Exception as ex:
                            material_status = None
                    if len(l1) != len(all_videos) or False in l1:
                        new_dict[f"course_{i}"] = "Ongoing"
                        ongoing_coures_uuid.append(i)
                course_data = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{'uuid__in':ongoing_coures_uuid})
            except Exception as ex:
                pass

        elif var == "completed":
            new_dict = OrderedDict()
            try:
                completed_coures_uuid = []
                for i in list(course_data_uuid): 
                    try:
                        var = getattr(models,"CourseMaterial").objects.get(**{'course__uuid':i})
                        all_videos = var.video_files.all()
                    except Exception as ex:
                        var = None
                        continue
                    l1 = []
                    for j in all_videos:
                        try:
                            material_status = getattr(models,"CourseMaterialStatus").objects.get(**{'user_email':email_id, 'video_id':j.uuid})
                            l1.append(material_status.is_complete)
                        except Exception as ex:
                            material_status = None
                    if len(l1) == len(all_videos) and False not in l1:
                        new_dict[f"course_{i}"] = "Completed"
                        completed_coures_uuid.append(i)
                course_data = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{'uuid__in':completed_coures_uuid})
            except Exception as ex:
                pass
                
        try:
            cat = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
            try:
                area_of_interest = cat.area_of_interest.split(",")
            except Exception as ex:
                area_of_interest = cat.area_of_interest.split()
            try:
                a = cat.course_category.split(",")
            except Exception as ex:
                a = cat.course_category.split()
        except Exception as ex:
            pass
        organization_domain = email_id.split('@')[1]
        try:
            data_category = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False, COURSE_FOR_ORGANIZATION:False}).filter(Q(course_category__category_name__in = area_of_interest) | Q(course_name__in = area_of_interest)).exclude(course_name__in=enroll_data).order_by("-organization_domain")
        except Exception as ex:
            data_category = None
        if serializer := CourseDetailsSerializer(course_data, many=True):
            if serializer1 := CourseDetailsSerializer(data_category, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data, "related_course":serializer1.data, "final_course_status":new_dict}, status=status.HTTP_200_OK)   
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class EventEnrollView(APIView):
    def get(self, request):
        email_id =  get_user_email_by_token(request)
        if email_id:
            try:
                enroll_data = getattr(models,EVENTAD_ENROLL_TABLE).objects.filter(**{'user_profile__email_id':email_id}).values_list("event_name", flat = True)
            except Exception as ex:
                enroll_data = None

            try:
                event_data = getattr(models,EVENT_AD_TABLE).objects.filter(**{'event_name__in':list(enroll_data)}).order_by("-created_date_time")
            except:
                event_data = None

            try:
                category = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                a = category.course_category.split(",")
            except Exception as ex:
                a = category.course_category.split()
            try:
                category_event = getattr(models,EVENT_AD_TABLE).objects.filter(**{STATUS_ID:1, IS_DELETED:False}).filter(Q(event_name__in = a) | Q(event_category__in = a)).exclude(event_name__in = enroll_data).order_by("-created_date_time")
            except:
                category_event = None

            if serializer := EventAdSerializer(event_data, many=True):
                if serializer1 := EventAdSerializer(category_event, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data, "related_event":serializer1.data}, status=status.HTTP_200_OK)
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({STATUS: ERROR, DATA: "Cound not find email Id from token."}, status=status.HTTP_400_BAD_REQUEST)



class CourseMaterialStatus(APIView):
    def post(self, request):
        email_id =  get_user_email_by_token(request)
        video_id = request.POST.get("video_id")
        try:
            try:
                data = getattr(models,"CourseMaterialStatus").objects.get(**{'user_email':email_id, "video_id":video_id})
            except Exception as ex:
                data = None
            if data is not None:
                if data.is_complete != True:
                    record_map = {}
                    if request.POST.get("duration"):
                        record_map["duration"] = request.POST.get("duration")
                    else:
                        record_map["duration"] = data.duration

                    if request.POST.get("is_complete"):
                        record_map["is_complete"] = json.loads(request.POST.get("is_complete"))
                    else:
                        record_map["is_complete"] = data.is_complete

                    for key, value in record_map.items():
                        setattr(data, key, value)
                    data.save()
                    
            else:
                record_map = {}
                record_map = {
                    "user_email" : email_id,
                    "video_id" : video_id,
                }
                if request.POST.get("is_complete"):
                    record_map["is_complete"] = request.POST.get("is_complete")

                if request.POST.get("duration"):
                    record_map["duration"] = json.loads(request.POST.get("duration"))
                getattr(models,"CourseMaterialStatus").objects.update_or_create(**record_map)
        except Exception as ex:
            pass
        return Response({STATUS: SUCCESS, DATA: "Material Status Added Successfully"}, status=status.HTTP_200_OK)


class Whats_On_Eddi(APIView):
    def get(self, request):
        data = getattr(models,"WhatsonEddiCMS").objects.all()
        if serializer := WhatsOnEddiSerializer(data, many=True):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class Whats_On_Eddi_sv(APIView):
    def get(self, request):
        data = getattr(models,"WhatsonEddiCMS_SV").objects.all()
        if serializer := WhatsOnEddiSerializer_sv(data, many=True):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class CourseRating(APIView):
    def post(self, request, uuid=None):
        email_id = get_user_email_by_token(request)
        try:
            user = getattr(models,USER_PROFILE_TABLE).objects.get(**{"email_id":email_id})
            course = getattr(models,COURSEDETAILS_TABLE).objects.get(**{"uuid":uuid})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in getting user or course"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = getattr(models,"CourseRating").objects.get(**{"user":user, "course_name":course})
        except Exception as ex:
            data = None
        if data is None:
            try:
                star1 = request.POST.get("star", None)
                record_map = {}
                record_map = {
                    "user" : user,
                    "course_name" : course,
                    "star" : "{:.1f}".format(int(star1)),
                    "comment" : request.POST.get("comment", None)
                }

            except Exception as ex:
                pass
                return Response({STATUS: ERROR, DATA: "Error in record map"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                getattr(models,"CourseRating").objects.update_or_create(**record_map)
                try:
                    admin_email = getattr(models,USERSIGNUP_TABLE).objects.get(**{"user_type__user_type":"Admin"})
                except Exception as ex:
                    pass
                if course.created_by == "Admin":
                    try:
                        html_path = "user_rate_to_admin.html"
                        fullname = f'{user.first_name} {user.last_name}'
                        context_data = {'supplier_name':course.supplier.first_name,'fullname':fullname,"course_name":course.course_name,'star':"{:.1f}".format(int(request.POST.get("star"))),"review":request.POST.get("comment")}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (admin_email.email_id,)
                        email_msg = EmailMessage('Welcome to Eddi',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        print("TRUE")
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
                        pass
                return Response({STATUS: SUCCESS, DATA: "User Rating Saved Successfully"}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error in Saving Data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                record_map = {}
                record_map = {
                    "star" : request.POST.get("star", data.star),
                    "comment" : request.POST.get("comment", data.comment)
                }
                for key, value in record_map.items():
                    setattr(data, key, value)
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Course Rating Edited Successfully"}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({STATUS: ERROR, DATA: "Error in Saving Edited Data"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, uuid=None):
        email_id = get_user_email_by_token(request)
        try:
            user = getattr(models,USER_PROFILE_TABLE).objects.get(**{"email_id":email_id})
            course = getattr(models,COURSEDETAILS_TABLE).objects.get(**{"uuid":uuid})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in getting user or course"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = getattr(models,"CourseRating").objects.get(**{"user":user, "course_name":course})
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in getting CourseRating"}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer := CourseRatingSerializer(data):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        return Response({STATUS: SUCCESS, DATA: serializer.error}, status=status.HTTP_200_OK)


class Notification(APIView):
    def put(self, request):
        email_id = get_user_email_by_token(request)
        receiver = request.POST.get("receiver")
        is_clear = json.loads(request.POST.get("is_clear"))
        if request.POST.get("is_clear"):
            try:
                data = getattr(models,"Notification").objects.filter(**{"receiver__icontains":receiver})
                data.delete()
            except Exception as ex:
                print(ex,"exexe")
    
    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,"Notification").objects.filter(**{"receiver__icontains":email_id})
        except Exception as ex:
            print(ex,"exexe")
            data = None
        if serializer := NotificationSerializer(data, many=True):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        return Response({STATUS: SUCCESS, DATA: serializer.error}, status=status.HTTP_200_OK)




