from email.mime.image import MIMEImage
import os
from xhtml2pdf import pisa
import random
from random import shuffle
from io import BytesIO
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from .serializers import *
from eddi_app import models
from eddi_app.constants.constants import *
from eddi_app.constants.table_name import *
from datetime import date
from django.db.models import Q
from collections import OrderedDict
from django.utils.timezone import make_aware
from django.contrib.auth.hashers import make_password, check_password
from .supplier_views import *
from uuid import uuid4
import stripe # 2.68.0
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from .notification import send_notification
from translate import Translator
import datetime
from datetime import date
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.db import connection


class PayByInvoice(APIView):
    def post(self, request):
        email_id =  get_user_email_by_token(request)
        record_map = {}
        if request.POST.get("product_type") == "course":
            course = getattr(models,COURSEDETAILS_TABLE).objects.get(**{COURSE_NAME:request.POST.get(COURSE_NAME)})
        else:
            course = None
        try:
            record_map = {
            "invoice_method" : request.POST.get("InvoiceMethod"),
            "dob" : request.POST.get("Dob"),
            "student_name" : request.POST.get("NameOfStudent"),
            "personal_number" : request.POST.get("PersonalNumber"),
            "organization_name" : request.POST.get("OrganizationName"),
            "organization_number" : request.POST.get("OrganizationNumber"),
            "street_number" : request.POST.get("StreetNumber"),
            "reference" : request.POST.get("Reference"),
            "zip_code" : request.POST.get("Zip"),
            "contry" : request.POST.get("Country"),
            "city" : request.POST.get("City"),
            # "invoice_address" : request.POST.get("invoiceAddress"),
            "student_email" : email_id,
            "invoice_email" : request.POST.get("InvoiceEmail"),
            "price" : request.POST.get("price"),
            "payment_mode" : request.POST.get("payment_mode"),
            "product_type" : request.POST.get("product_type"),
            }
            if course != None:
                record_map["course"] = course
            if request.POST.get("product_type") == "event":
                record_map["product_name"] = request.POST.get("event_name")
            else:
                record_map["product_name"] = request.POST.get("course_name")

            # try:
            #     var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, "course__course_name":course_name,STATUS:'Success'})
            #     if var is not None:
            #         return Response({MESSAGE: ERROR, DATA: "You’ve already enrolled", DATA_SV:"Du är redan registrerad"}, status=status.HTTP_400_BAD_REQUEST)
            # except:
            #     pass


            getattr(models,"PaybyInvoice").objects.update_or_create(**record_map)
            try:
                vat = getattr(models,"InvoiceVATCMS").objects.all().values_list("vat_value", flat=True)
                vat_val = int(vat[0])
                invoice_number = random.randrange(100000,999999)
                    
                user_data = getattr(models, USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
                amount = float(request.POST.get("price"))
                total_price = int(amount) + (int(amount)*vat_val)/100
                try:
                     
                    if record_map["invoice_method"] == "PayByMe":
                        context_data = {"student_name": request.POST.get("NameOfStudent"), "personal_number":request.POST.get("PersonalNumber"),"street_number":request.POST.get("StreetNumber"), "reference":request.POST.get("Reference"), "zip_code":request.POST.get("Zip"), "contry":request.POST.get("City"), "city" : request.POST.get("City"),"student_email" : email_id,"price" : request.POST.get("price"), "payment_mode" : request.POST.get("payment_mode"), "product_type" : request.POST.get("product_type"),"course_name":course.course_name,"vat":vat_val,"total_fees":total_price,"invoice_number":invoice_number,"issue_date":date.today(),"course_name":course.course_name,} 
                        template = get_template('invoice_temp_pbi_student.html').render(context_data)
                   
                    elif record_map["invoice_method"] == "PayByOrg":
                        context_data = {"student_name": request.POST.get("NameOfStudent"), "personal_number":request.POST.get("PersonalNumber"),"street_number":request.POST.get("StreetNumber"), "reference":request.POST.get("Reference"), "zip_code":request.POST.get("Zip"), "contry":request.POST.get("City"), "city" : request.POST.get("City"),"student_email" : email_id,"price" : request.POST.get("price"), "payment_mode" : request.POST.get("payment_mode"), "product_type" : request.POST.get("product_type"),"course_name":course.course_name,"vat":vat_val,"total_fees":total_price,"invoice_number":invoice_number,"issue_date":date.today(),"course_name":course.course_name,} 
                        template = get_template('invoice_temp_pbi_student.html').render(context_data)
                    
                    result = BytesIO()
                    pdf = pisa.pisaDocument(BytesIO(template.encode("UTF-8")), result)#, link_callback=fetch_resources)
                    pdf = result.getvalue()
                    filename = f'Invoice-{invoice_number}.pdf'
                
                except Exception as e:
                    print(e,"pdf exp")
                    pass

                if request.POST.get("product_type") == "course":
                    print("Course")
                    record_map1 = {}
                    record_map1 = {
                        "course_id" : course.id,
                        "email_id" : email_id,
                        "user_name" : f"{user_data.first_name} {user_data.last_name}",
                        "amount" : amount,
                        "payment_mode" : "PayByInvoice",
                    }
                    record_map1[IS_APPROVED_ID] = 2
                    record = {
                            "invoice_number" : invoice_number,
                            "user_address" : "Address",
                            "user_email" : email_id,
                            "course_name" : course.course_name,
                            "vat_charges" : vat_val,
                            "invoice_pdf" : "/var/www/html/eddi-backend/media/"+filename,
                            }
                    invoice_data = getattr(models,"InvoiceData").objects.update_or_create(**record)
                    record_map1["invoice"] = invoice_data[0]
                    getattr(models,USER_PAYMENT_DETAIL).objects.update_or_create(**record_map1)
                    
                    try:
                        if course.supplier.user_type.user_type == SUPPLIER_S:
                            supplier_data = getattr(models,'SupplierAccountDetail').objects.get(**{'supplier':course.supplier})
                            total_earnings = supplier_data.total_earnings + float(record_map2["amount"])
                            setattr(supplier_data,'total_earnings',total_earnings)
                            supplier_data.save()
                    except Exception as ex:
                        pass
                   
                else:
                    print("Event")
                    event = getattr(models,EVENT_AD_TABLE).objects.get(**{EVENT_NAME:request.POST.get("event_name")})
                    record_map2 = {}
                    record_map2 = {
                        "admin_name" : event.admin_name,
                        "event_name" : request.POST.get("event_name"),
                        "email_id" : email_id,
                        "user_name" : f"{user_data.first_name} {user_data.last_name}",
                        "amount" : amount,
                        "payment_mode" : "PayByInvoice",
                    }
                    record_map2[IS_APPROVED_ID] = 2
                    record = {
                        "invoice_number" : invoice_number,
                        "user_address" : "Address",
                        "user_email" : email_id,
                        "course_name" : course.course_name,
                        "vat_charges" : vat_val,
                        "invoice_pdf" : "/var/www/html/eddi-backend/media/"+filename,
                        }
                    invoice_data = getattr(models,"InvoiceDataEvent").objects.update_or_create(**record)
                    record_map2["invoice"] = invoice_data[0]
                    getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.update_or_create(**record_map2)
                   
                try:
                   
                    instance = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})    
                    if record_map["invoice_method"] == "PayByMe":
                        if request.POST.get("product_type") == "course":
                            # course = getattr(models,COURSEDETAILS_TABLE).objects.get(**{COURSE_NAME:request.POST.get(COURSE_NAME)})   
                            fullname = f'{instance.first_name}'
                            recipient_list = (email_id,)
                            recipient_list1 = (course.supplier.email_id,)
                            context_data1 = {"fullname":fullname}
                            context_data2 = {"fullname":course.supplier.first_name +" "+ course.supplier.last_name} 
                           
                             
                        else:
                            event = getattr(models,EVENT_AD_TABLE).objects.get(**{EVENT_NAME:request.POST.get("event_name")})
                            fullname = f'{instance.first_name}'
                            recipient_list = (email_id,)
                            recipient_list1 = (course.supplier.email_id,)
                            context_data1 = {"fullname":fullname}
                            context_data2 = {"fullname":event.admin_name} 
                            
                        try:                               
                            html_path = "pay_by_invoice.html" 
                            email_html_template1 = get_template(html_path).render(context_data1)
                            email_html_template2 = get_template(html_path).render(context_data2)
                            email_from = settings.EMAIL_HOST_USER
                            recipient_list = recipient_list  
                                        
                            try:
                                path = 'eddi_app'
                                img_dir = 'static'
                                image = 'Logo.png'
                                file_path = os.path.join(path,img_dir,image)
                                with open(file_path,'rb') as f:
                                    img = MIMEImage(f.read())
                                    img.add_header('Content-ID', '<{name}>'.format(name=image))
                                    img.add_header('Content-Disposition', 'inline', filename=image)
                            except Exception as e:
                                print(e,"filee")
                                pass
                            email_msg = EmailMessage('Payment Invoice!!',email_html_template1,email_from,recipient_list)
                            email_msg1 = EmailMessage('Payment Invoice!!',email_html_template2,email_from,recipient_list1)
                            email_msg.content_subtype = 'html'
                            email_msg.attach(img)
                            email_msg1.content_subtype = 'html'
                            email_msg1.attach(img)
                            try:
                                email_msg.attach(filename, pdf, "application/pdf")                         
                                email_msg1.attach(filename, pdf, "application/pdf")                         
                            except Exception as e:
                                print(e,"attachhh")
                                pass
                            email_msg.send(fail_silently=False)
                            email_msg1.send(fail_silently=False)
                        except Exception as e:
                            print(e)
                            

                    elif record_map["invoice_method"] == "PayByOrg":
                        if request.POST.get("product_type") == "course":   
                            fullname = f'{instance.first_name}'
                            recipient_list = (email_id,)
                            recipient_list1 = (course.supplier.email_id,)
                            recipient_list2 = (request.POST.get("InvoiceEmail"))
                            context_data1 = {"fullname":fullname}
                            context_data2 = {"fullname":course.supplier.first_name +" "+ course.supplier.last_name} 
                            context_data3 = {"fullname":request.POST.get("OrganizationName")}
                        
                        else:
                            event = getattr(models,EVENT_AD_TABLE).objects.get(**{EVENT_NAME:request.POST.get("event_name")})
                            fullname = f'{instance.first_name}'
                            recipient_list = (email_id,)
                            recipient_list1 = (course.supplier.email_id,)
                            recipient_list2 = (request.POST.get("InvoiceEmail"))
                            context_data1 = {"fullname":fullname}
                            context_data2 = {"fullname":course.supplier.first_name +" "+ course.supplier.last_name} 
                            context_data3 = {"fullname":request.POST.get("OrganizationName")}
                        

                        try:                               
                            html_path = "pay_by_invoice.html" 
                            email_html_template1 = get_template(html_path).render(context_data1)
                            email_html_template2 = get_template(html_path).render(context_data2)
                            email_html_template3 = get_template(html_path).render(context_data3)
                            email_from = settings.EMAIL_HOST_USER
                                        
                            try:
                                path = 'eddi_app'
                                img_dir = 'static'
                                image = 'Logo.png'
                                file_path = os.path.join(path,img_dir,image)
                                with open(file_path,'rb') as f:
                                    img = MIMEImage(f.read())
                                    img.add_header('Content-ID', '<{name}>'.format(name=image))
                                    img.add_header('Content-Disposition', 'inline', filename=image)
                            except Exception as e:
                                print(e,"filee")
                                pass
                            email_msg = EmailMessage('Payment Invoice!!',email_html_template1,email_from,recipient_list)
                            email_msg1 = EmailMessage('Payment Invoice!!',email_html_template2,email_from,recipient_list1)
                            email_msg2 = EmailMessage('Payment Invoice!!',email_html_template3,email_from,recipient_list2)
                            email_msg.content_subtype = 'html'
                            email_msg.attach(img)
                            email_msg1.content_subtype = 'html'
                            email_msg1.attach(img)
                            email_msg2.content_subtype = 'html'
                            email_msg2.attach(img)
                            try:
                                email_msg.attach(filename, pdf, "application/pdf")                         
                                email_msg1.attach(filename, pdf, "application/pdf")                         
                                email_msg2.attach(filename, pdf, "application/pdf")                         
                            except Exception as e:
                                print(e,"attachhh")
                                pass
                            email_msg.send(fail_silently=False)
                            email_msg1.send(fail_silently=False)
                            email_msg2.send(fail_silently=False)
                        except Exception as e:
                            print(e)

                        # context_data = {'fullname':fullname, "student_name": request.POST.get("NameOfStudent"), "personal_number":request.POST.get("PersonalNumber"), "organization_name":request.POST.get("OrganizationName"), "organization_number":request.POST.get("OrganizationNumber"), "street_number":request.POST.get("StreetNumber"), "reference":request.POST.get("Reference"), "zip_code":request.POST.get("Zip"), "contry":request.POST.get("City"), "city" : request.POST.get("City"),"email_id" : email_id,"price" : request.POST.get("price"), "payment_mode" : request.POST.get("payment_mode"), "product_type" : request.POST.get("product_type"),"course_name":course.course_name,"vat":vat_val,"total_fees":total_price}
                        # template = get_template('invoice_temp_pbi.html').render(context_data)
                        
                   
               
                        
                        # if record_map["invoice_method"] == "PayByMe":
                           
                        # elif record_map["invoice_method"] == "PayByOrg":
                        #     recipient_list = (record_map["email_id"],instance.email_id)
                        #     fullname = f'{event.admin_name}'
                   
                   

                   
                    # html_path = "pay_by_invoice.html"
                    # context_data = {'fullname':fullname, "student_name": request.POST.get("NameOfStudent"), "personal_number":request.POST.get("PersonalNumber"), "organization_name":request.POST.get("OrganizationName"), "organization_number":request.POST.get("OrganizationNumber"), "street_number":request.POST.get("StreetNumber"), "reference":request.POST.get("Reference"), "zip_code":request.POST.get("Zip"), "contry":request.POST.get("City"), "city" : request.POST.get("City"),"invoice_address" : request.POST.get("invoiceAddress"),"email_id" : email_id,"price" : request.POST.get("price"), "payment_mode" : request.POST.get("payment_mode"), "product_type" : request.POST.get("product_type")}
                    # email_html_template = get_template(html_path).render(context_data)
                    # email_from = settings.EMAIL_HOST_USER
                    # email_msg = EmailMessage('Pay By Invoice!!',email_html_template,email_from,recipient_list)
                    # email_msg.content_subtype = 'html'
                    # path = 'eddi_app'
                    # img_dir = 'static'
                    # image = 'Logo.png'
                    # file_path = os.path.join(path,img_dir,image)
                    # with open(file_path,'rb') as f:
                    #     img = MIMEImage(f.read())
                    #     img.add_header('Content-ID', '<{name}>'.format(name=image))
                    #     img.add_header('Content-Disposition', 'inline', filename=image)
                    # email_msg.attach(img)
                    # email_msg.send(fail_silently=False)
                except Exception as e:
                    print(e,"exx")
                    pass
                return Response({STATUS: SUCCESS, DATA: "Information successfully added", DATA_SV:"Informationen har nu sparats"}, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response({MESSAGE: ERROR, DATA:"Something went wrong", DATA_SV:"Något gick fel"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({MESSAGE: ERROR, DATA: "Something went wrong", DATA_SV:"Något gick fel"}, status=status.HTTP_400_BAD_REQUEST)



@permission_classes([AllowAny])
class Save_stripe_info(APIView):
    def post(self, request, *args, **kwargs):
        if request.method == POST_METHOD:
            intent = None
            email_id = request.POST.get(EMAIL_ID)
            amount = request.POST.get(PRICE)
            payment_method_id = request.POST.get(PAYMENT_METHOD_ID)
            course_name = request.POST.get(COURSE_NAME)
            extra_msg = ''
            try:
                var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, "course__course_name":course_name,STATUS:'Success'})
                if var is not None:
                    return Response({MESSAGE: ERROR, DATA: "You’ve already enrolled", DATA_SV:"Du är redan registrerad"}, status=status.HTTP_400_BAD_REQUEST)
            except:
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
                    # intent = stripe.PaymentIntent.create(
                    #     amount=int(float(amount)*100),
                    #     currency='usd',
                    #     description='helllo',
                    #     customer=customer['id'],
                    #     payment_method_types=["card"],
                    #     payment_method=payment_method_id,
                    #     confirm=True)
                    course = getattr(models,COURSEDETAILS_TABLE).objects.get(**{COURSE_NAME:course_name})
                    if course.supplier.user_type.user_type == SUPPLIER_S:
                        supplier_amount = int(float(amount)*100) - int(float(amount)*100*0.02)
                        intent = stripe.PaymentIntent.create(
                            # on_behalf_of = getattr(models,'SupplierAccountDetail').objects.get(**{'supplier':course.supplier}).account_id,
                            # transfer_data = {
                            #     'destination': getattr(models,'SupplierAccountDetail').objects.get(**{'supplier':course.supplier}).account_id,
                            # },
                            amount=int(float(amount)*100),
                            currency='sek',
                            description=f'Course = {course_name},User = {email_id}',
                            customer=customer['id'],
                            payment_method_types=["card"],
                            payment_method=payment_method_id,
                            # application_fee_amount=int(float(amount)*100*0.5),
                            confirm=True,
                        )
                        print(intent,"intent")
                        transfer = stripe.Transfer.create(
                            amount=supplier_amount,
                            currency='sek',
                            destination=getattr(models,'SupplierAccountDetail').objects.get(**{'supplier':course.supplier}).account_id,
                        )
                    else:
                        intent = stripe.PaymentIntent.create(
                            amount=int(float(amount)*100),
                            currency='usd',
                            description=f'Course = {course_name},User = {email_id}',
                            customer=customer['id'],
                            payment_method_types=["card"],
                            payment_method=payment_method_id,
                            confirm=True)
                   
                    
                except Exception as ex:
                    print(ex)
                    return Response({MESSAGE: ERROR, DATA: "Something went wrong", DATA_SV:"Något gick fel"}, status=status.HTTP_400_BAD_REQUEST) 
                try:
                    instance = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                    vat = getattr(models,"InvoiceVATCMS").objects.all().values_list("vat_value", flat=True)
                    vat_val = int(vat[0])
                    html_path = INVOICE_TO_USER
                    fullname = f'{instance.first_name} {instance.last_name}'
                    context_data = {'fullname':fullname, "course_name":course_name,"total":int(float(amount)) + (int(float(amount))*vat_val)/100}
                    email_html_template = get_template(html_path).render(context_data)
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = (instance.email_id,)
                    invoice_number = random.randrange(100000,999999)
                    context_data1 = {"invoice_number":invoice_number,"user_address":"User Address","issue_date":date.today(),"course_name":course_name,"course_fees": amount, "vat":vat_val, "total":int(float(amount)) + (int(float(amount))*vat_val)/100}
                    template = get_template('invoice.html').render(context_data1)
                    try: 
                        result = BytesIO()
                        pdf = pisa.pisaDocument(BytesIO(template.encode("UTF-8")), result)#, link_callback=fetch_resources)
                        pdf = result.getvalue()
                        filename = f'Invoice-{invoice_number}.pdf'
                    except:
                        pass
                    record = {}
                    try: 
                        record = {
                            "invoice_number" : invoice_number,
                            "user_address" : "Address",
                            "user_email" : instance.email_id,
                            "course_name" : course_name,
                            "vat_charges" : vat_val,
                            "invoice_pdf" : "/var/www/html/eddi-backend/media/"+filename,
                        }
                        getattr(models,"InvoiceData").objects.update_or_create(**record)
                    except:
                        pass
                    try:
                        path = 'eddi_app'
                        img_dir = 'static'
                        image = 'Logo.png'
                        file_path = os.path.join(path,img_dir,image)
                        with open(file_path,'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', '<{name}>'.format(name=image))
                            img.add_header('Content-Disposition', 'inline', filename=image)
                    except:
                        pass
                    email_msg = EmailMessage('Payment received successfully!!',email_html_template,email_from,recipient_list)
                    email_msg.content_subtype = 'html'
                    email_msg.attach(img)
                    try:
                        email_msg.attach(filename, pdf, "application/pdf")                         
                    except:
                        pass
                    email_msg.send(fail_silently=False)
                except:
                    pass
                return Response({MESSAGE: SUCCESS, DATA: {PAYMENT_INTENT:intent, EXTRA_MSG: extra_msg}}, status=status.HTTP_200_OK)
            except:
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
                        return Response({MESSAGE: ERROR, DATA: "You've already enrolled", DATA_SV:"Du är redan registrerad "}, status=status.HTTP_400_BAD_REQUEST)
                except:
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
                        amount=int(float(amount)*100),
                        currency='usd',
                        description='helllo',
                        customer=customer['id'],
                        payment_method_types=["card"],
                        payment_method=payment_method_id,
                        confirm=True)
                    except:
                        return Response({MESSAGE: ERROR, DATA: "Something went wrong", DATA_SV:"Något gick fel"}, status=status.HTTP_400_BAD_REQUEST)

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
                        except:
                            pass
                        record = {}
                        try:
                            record = {
                            "invoice_number" : invoice_number,
                            "user_address" : "Address",
                            "user_email" : instance.email_id,
                            "event_name" : event_name,
                            "vat_charges" : vat_val,
                            "invoice" :  "/var/www/html/eddi-backend/media/"+filename,
                            }
                            getattr(models,"InvoiceDataEvent").objects.update_or_create(**record)
                        except:
                            pass
                        path = 'eddi_app'
                        img_dir = 'static'
                        image = 'Logo.png'
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
                    except:
                        pass
                    return Response({MESSAGE: SUCCESS, DATA: {PAYMENT_INTENT:intent, EXTRA_MSG: extra_msg}}, status=status.HTTP_200_OK,)
                except:
                    return Response({MESSAGE: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)
            return Response({MESSAGE: 'Invalid request', DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])   
class UserSignupView(APIView):
    def post(self, request):
        record_map = {}
        try:
            user_type_id = getattr(models,USER_TYPE_TABLE).objects.only(ID).get(**{USER_TYPE:request.POST.get(USER_TYPE,None)})
        except:
            return Response({STATUS:ERROR, DATA: "Something went wrong", DATA_SV:"Något gick fel"}, status=status.HTTP_400_BAD_REQUEST)
        
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
        except:
            return Response({STATUS: ERROR, DATA: "Password or social login needed", DATA_SV:"Lösenord eller login genom sociala medier behövs"}, status=status.HTTP_400_BAD_REQUEST)

        record_map[CREATED_AT] = make_aware(datetime.datetime.now())
        record_map[CREATED_BY] = 'admin'
        
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.update_or_create(**record_map)
            # record_data1 = {
            #         DEVICE_TOKEN:request.POST.get(DEVICE_TOKEN,None),
            #         USER_TYPE:data[0]
            #     }
            # getattr(models,DEVICE_TOKEN_TABLE).objects.create(**record_data1)
        except Exception as ex:
            print(ex)
            return Response({STATUS: ERROR, DATA: "Something went wrong", DATA_SV:"Något gick fel"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Congratulations, your account has been created successfully!", DATA_SV:"Grattis, ditt konto är nu skapat"}, status=status.HTTP_200_OK)

class GetUserDetails(APIView):
    def post(self, request):
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.filter(**{'user_type__user_type':request.POST.get('user_type')})
            if serializer := UserSignupSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: "Data not found", DATA_SV:"Ingen information tillgänglig"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Information added successfully", DATA_SV:"Informationen har sparats"}, status=status.HTTP_200_OK)


    def get(self, request,uuid = None):
        email_id =  get_user_email_by_token(request)
        if uuid:
            try:
                data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{UUID:uuid})
                user_type = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id}).user_type.user_type
                if user_type == ADMIN_S:
                    if userSignup_serializer :=  UserSignupSerializer(data):
                    # Below Line : To make Active or Inactive to Particular user or supplier 
                        if data.user_type.user_type =='User':
                            try:
                                profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:data.email_id})
                            except:
                                return Response({STATUS: ERROR, DATA: "Something went wrong", DATA_SV:"Något gick fel"}, status=status.HTTP_400_BAD_REQUEST)

                            try:
                                course_enrolled = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{"email_id":data.email_id, "status":"Success"}).values_list("course__course_name", flat=True)
                                course_list = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"course_name__in":course_enrolled})
                            except:
                                return Response({STATUS: ERROR, DATA: "Something went wrong", DATA_SV:"Något gick fel"}, status=status.HTTP_400_BAD_REQUEST)
                                
                            if serializer := UserProfileSerializer(profile_data):
                                if serializer2 := CourseDetailsSerializer(course_list, many=True):
                                    return Response({STATUS: SUCCESS, DATA: [serializer.data,userSignup_serializer.data], "course_list":serializer2.data}, status=status.HTTP_200_OK)
                                else:
                                    return Response({STATUS: ERROR, DATA: serializer2.errors}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                        elif data.user_type.user_type ==SUPPLIER_S:
                            try:
                                supplier_all_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":data.email_id}).values_list("course_name", flat=True)
                                individuals_useremail = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{"course__course_name__in":supplier_all_course, "status":"Success"}).values_list("email_id", flat=True)
                                # supplier_course_count = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":data.email_id}).count()
                                # enrolled_count = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{"course__course_name__in":supplier_all_course, "status":"Success"}).count()
                                supplier_course_count = supplier_all_course.count()
                                enrolled_count = individuals_useremail.count()
                                # print(individuals_useremail.count())
                                # print(supplier_all_course.count())
                                individuals_user = getattr(models,USER_PROFILE_TABLE).objects.filter(**{"email_id__in":individuals_useremail})
                            except:
                                return Response({STATUS: ERROR, DATA: "Something went wrong", DATA_SV:"Något gick fel"}, status=status.HTTP_400_BAD_REQUEST)

                            try:
                                try:
                                    organization_profile_data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:data.email_id})
                                except:
                                    organization_profile_data= None
                                try:
                                    supplier_profile_data = getattr(models,SUPPLIER_PROFILE_TABLE).objects.get(**{'supplier_email':data.email_id})
                                except:
                                    supplier_profile_data= None
                                print(len(connection.queries))
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
                            except:
                                return Response({STATUS: ERROR, DATA: "Something went wrong", DATA_SV:"Något gick fel"}, status=status.HTTP_400_BAD_REQUEST)
            
                        # elif getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == SUPPLIER_S:  
                        #     data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
                        #     if serializer := UserSignupSerializer(data):
                        #         return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                        #     else:
                        #         return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({STATUS: ERROR, DATA: serializer.errors, DATA: "Data not found", DATA_SV:"Ingen information tillgänglig"}, status=status.HTTP_400_BAD_REQUEST)


                elif user_type == SUPPLIER_S:
                    if userSignup_serializer :=  UserSignupSerializer(data):
                        if data.user_type.user_type =='User':
                            try:
                                profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:data.email_id})
                            except:
                                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
                            try:
                                course_enrolled = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{"email_id":data.email_id, "status":"Success"}).values_list("course__course_name", flat=True)
                                course_list = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"course_name__in":course_enrolled})
                            except:
                                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
                                
                            if serializer := UserProfileSerializer(profile_data):
                                if serializer2 := CourseDetailsSerializer(course_list, many=True):
                                    return Response({STATUS: SUCCESS, DATA: [serializer.data,userSignup_serializer.data], "course_list":serializer2.data}, status=status.HTTP_200_OK)
                                else:
                                    return Response({STATUS: ERROR, DATA: serializer2.errors}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                        
                        else:
                            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV: "Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({STATUS: ERROR, DATA: serializer.errors, DATA:"Data not found", DATA_SV:"Ingen information tillgänglig"}, status=status.HTTP_400_BAD_REQUEST)

            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
       
        else:
            try:
                all_data = getattr(models,USERSIGNUP_TABLE).objects.filter(**{IS_DELETED:False}).exclude(user_type__user_type="Admin")
            except:
                all_data = None
            if serializer := UserSignupSerializer(all_data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: SUCCESS, DATA:serializer.errors}, status=status.HTTP_200_OK)


    def put(self,request,uuid = None):
        email_id =  get_user_email_by_token(request)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        record_map1 = {}
        if getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == ADMIN_S:
            if request.POST.get("status"):
                if request.POST.get("status") == "Active":
                    record_map1[STATUS_ID] = 1
                    try:
                        html_path = USER_ACTIVATED
                        fullname = f'{user_data.first_name} {user_data.last_name}'
                        context_data = {'fullname':fullname}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (user_data.email_id,)
                        email_msg = EmailMessage('Account has been activated by the admin',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        print("TRUE")
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
                        html_path = USER_DEACTIVATED
                        fullname = f'{user_data.first_name} {user_data.last_name}'
                        context_data = {'fullname':fullname}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (user_data.email_id,)
                        email_msg = EmailMessage('Account has been deactivate by the Admin',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        print("TRUE")
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
                for key,value in record_map1.items():
                    setattr(user_data,key,value)
                user_data.save() 
                return Response({STATUS: SUCCESS, DATA: "Information successfully edited", DATA_SV:"Din information har nu ändrats"}, status=status.HTTP_200_OK)

        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data not found", DATA_SV:"Ingen information tillgänglig"}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({STATUS: SUCCESS, DATA: "Information successfully edited", DATA_SV:"Din information har nu ändrats"}, status=status.HTTP_200_OK)

    def delete(self,request,uuid = None):
        email_id =  get_user_email_by_token(request)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA:"Data not found", DATA_SV:"Ingen information tillgänglig"}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({STATUS: SUCCESS, DATA: "Information succesfully deleted", DATA_SV:"Data har nu raderats"}, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class UserLoginView(APIView):
    def post(self, request):
        email_id = request.POST.get(EMAIL_ID)
        password = request.POST.get(PASSWORD)
        # user_device_token = request.POST.get(DEVICE_TOKEN)
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
                    try:
                        d = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:request.POST.get(EMAIL_ID)})
                    except:
                        d = None
                    if d == None:
                        record_map['user_type_id'] = 2
                        try:
                            getattr(models,USERSIGNUP_TABLE).objects.update_or_create(**record_map)
                        except:
                            pass
                    try:
                        if d.is_login_from == "google":
                            try:
                                user_profile = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                                if user_profile:
                                    user_profile = True
                            except:
                                user_profile = False
                            token = NonBuiltInUserToken.objects.create(user_id = d.id)
                            d.modified_date_time = make_aware(datetime.datetime.now())
                            d.save()
                            return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:d.first_name, LAST_NAME:d.last_name} ,USER_TYPE:str(d.user_type),IS_FIRST_TIME_LOGIN: d.is_first_time_login,"is_resetpassword" : d.is_resetpassword,USER_PROFILE:user_profile,"Authorization":"Token "+ str(token.key)}, status=status.HTTP_200_OK)
                        else:
                            d.is_login_from = "google"
                            d.modified_date_time = make_aware(datetime.datetime.now())
                            d.save()
                            return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:d.first_name, LAST_NAME:d.last_name} ,USER_TYPE:str(d.user_type),IS_FIRST_TIME_LOGIN: d.is_first_time_login,"is_resetpassword" : d.is_resetpassword,USER_PROFILE:user_profile,"Authorization":"Token "+ str(token.key)}, status=status.HTTP_200_OK)
                    except:
                        pass
                except:
                    pass
                    
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id,IS_DELETED:False})
           
            token = NonBuiltInUserToken.objects.create(user_id = data.id)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
       
        try:
            user_profile = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
            if user_profile:
                user_profile = True
        except:
            user_profile = False
       
        # Supplier General Login
        try:
            if data.user_type.user_type == SUPPLIER_S:
               
                # Supplier Exception Cases
                try:
                    organization_data = getattr(models,SUPPLIER_ORGANIZATION_PROFILE_TABLE).objects.get(**{SUPPLIER_EMAIL:email_id})
                    if organization_data.rejection_count == 3:
                        return Response({STATUS: ERROR, DATA: "Your profile has been blocked. please contact to eddi support"}, status=status.HTTP_400_BAD_REQUEST)
                    if str(organization_data.is_approved.value) == "Pending" and organization_data.approved_once == False:
                        return Response({STATUS: ERROR, DATA: "Your profile is under review. You can't login until it's approved"}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    pass
              
                if not check_password(password, data.password):
                    return Response({STATUS: ERROR, DATA: "Invalid Credentials please try again!", DATA_SV:"Användarnamn eller lösenord stämmer inte, försök igen!"}, status=status.HTTP_400_BAD_REQUEST)
                if data.status.id == 2:
                    return Response({STATUS: ERROR, DATA: "Your account is temporarily inactivated, please contact eddi support", DATA_SV:"Ditt konto är tillfälligt inaktiverat, vänligen kontakta kundservice"}, status=status.HTTP_400_BAD_REQUEST)
                if check_password(password, data.password):
                    data.modified_date_time = make_aware(datetime.datetime.now())
                    data.save()
                    # record_data1 = {
                    #     DEVICE_TOKEN:user_device_token,
                    #     USER_TYPE:data
                    # }
                    # getattr(models,DEVICE_TOKEN_TABLE).objects.create(**record_data1)
                    return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:data.first_name, LAST_NAME:data.last_name} ,USER_TYPE:str(data.user_type),IS_FIRST_TIME_LOGIN: data.is_first_time_login,USER_PROFILE:user_profile,"is_resetpassword" : data.is_resetpassword,"Authorization":"Token "+ str(token.key),}, status=status.HTTP_200_OK)

        except:
            pass
        # General Admin Login
        try:
            if data.user_type.user_type == ADMIN_S:
                if not check_password(password, data.password):
                    return Response({STATUS: ERROR, DATA: "Invalid Credentials please try again!", DATA_SV:"Användarnamn eller lösenord stämmer inte, försök igen!"}, status=status.HTTP_400_BAD_REQUEST)
                if data.status.id == 2:
                    return Response({STATUS: ERROR, DATA: "Your account is temporarily inactivated, please contact eddi support", DATA_SV:"Ditt konto är tillfälligt inaktiverat, vänligen kontakta kundservice"}, status=status.HTTP_400_BAD_REQUEST)
                if check_password(password, data.password):
                    data.modified_date_time = make_aware(datetime.datetime.now())
                    data.save()
                    # record_data1 = {
                    #     DEVICE_TOKEN:user_device_token,
                    #     USER_TYPE:data
                    # }
                    # getattr(models,DEVICE_TOKEN_TABLE).objects.create(**record_data1)
                    return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:data.first_name, LAST_NAME:data.last_name} ,USER_TYPE:str(data.user_type),IS_FIRST_TIME_LOGIN: data.is_first_time_login,USER_PROFILE:user_profile,"is_resetpassword" : data.is_resetpassword,"Authorization":"Token "+ str(token.key),}, status=status.HTTP_200_OK)
        except:
            pass

        # User Login Cases
        try:
            if data.user_type.user_type == "User":
                if data.status.id == 2:
                    return Response({STATUS: ERROR, DATA: "Your account is temporarily inactivated, please contact eddi support", DATA_SV:"Ditt konto är tillfälligt inaktiverat, vänligen kontakta kundservice"}, status=status.HTTP_400_BAD_REQUEST)
                if not check_password(password, data.password):
                    return Response({STATUS: ERROR, DATA: "Invalid Credentials please try again!", DATA_SV:"Användarnamn eller lösenord stämmer inte, försök igen!"}, status=status.HTTP_400_BAD_REQUEST)
                if data.is_active == True:
                    data.modified_date_time = make_aware(datetime.datetime.now())
                    data.save()

                    # print(datetime.datetime.now())
                    # print(str(data.modified_date_time).split("+")[0])
                    # a = datetime.datetime.strptime(str(data.modified_date_time).split("+")[0], '%Y-%m-%d %H:%M:%S.%f')
                    # # print(a, "a")
                    # time_diff = datetime.datetime.now() - datetime.datetime.strptime(str(data.modified_date_time).split("+")[0], '%Y-%m-%d %H:%M:%S.%f')
                    # print(type(time_diff.seconds), "timeeeeeeeeeeeee")
                    # print(divmod(time_diff.seconds, 3600)[0] , "timeeeeeeeeeeeee")
                    print(user_profile)
                    # record_data1 = {
                    #     DEVICE_TOKEN:user_device_token,
                    #     USER_TYPE:data
                    # }
                    # getattr(models,DEVICE_TOKEN_TABLE).objects.create(**record_data1)
                    # getattr(models,DEVICE_TOKEN_TABLE).objects.create(device_token=user_device_token)
                    return Response({STATUS: SUCCESS, DATA: True, DATA: {FIRST_NAME:data.first_name, LAST_NAME:data.last_name} ,USER_TYPE:str(data.user_type),IS_FIRST_TIME_LOGIN: data.is_first_time_login,USER_PROFILE:user_profile,"is_resetpassword" : data.is_resetpassword,"Authorization":"Token "+ str(token.key),}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: "User is not authorized", DATA_SV:"Du kan inte utföra denna handling"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({STATUS: ERROR, DATA: "Please verify your account via your email", DATA_SV:"Vänligen verifiera ditt konto via din email"}, status=status.HTTP_400_BAD_REQUEST)



@permission_classes([AllowAny])
class ForgetPasswordView(APIView):
    def post(self, request,uuid = None):
        email_id = request.POST.get(EMAIL_ID)
        request.session['forget-password'] = email_id
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id,STATUS_ID:1,IS_DELETED:False})
            print(data.uuid)
        except:
            return Response({STATUS: ERROR, DATA: "You are not a registered user please contact eddi support", DATA_SV:"Vi kan inte hitta ditt konto, försök igen eller kontakta kundtjänst"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if data:
                if request.session.has_key('forget-password'):
                    if data.user_type.user_type == "User":
                        html_path = RESETPASSWORD_HTML
                        fullname = data.first_name + " " + data.last_name
                        context_data = {"final_email": email_id,"fullname":fullname,"uuid": data.uuid}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (email_id,)
                        email_msg = EmailMessage('Forgot Password',email_html_template,email_from,recipient_list)
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
                    

                    if data.user_type.user_type == SUPPLIER_S or data.user_type.user_type == ADMIN_S:
                        html_path = RESETPASSWORDSupplierAdmin_HTML
                        fullname = data.first_name + " " + data.last_name
                        context_data = {"uuid": data.uuid,"final_email": email_id,"fullname":fullname}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (email_id,)
                        email_msg = EmailMessage('Forgot Password',email_html_template,email_from,recipient_list)
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
        except:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)
                

@permission_classes([AllowAny])
class ResetPasswordView(APIView):
    def post(self,request):
        email_id = request.POST.get(EMAIL_ID)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id,STATUS_ID:1,IS_DELETED:False})
            password = request.POST.get(PASSWORD)
            if check_password(password, data.password):
                return Response({STATUS: ERROR, DATA: "You have already used this password, please choose an other one", DATA_SV:"Du har redan använt detta lösenord, vänligen välj ett nytt"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            data = None
        try:
            if data:
                setattr(data,PASSWORD,make_password(password))
                setattr(data,"is_resetpassword",False)
                setattr(data,MODIFIED_AT,make_aware(datetime.datetime.now()))
                setattr(data,MODIFIED_BY,'admin')
                data.uuid = uuid4()
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Password changed successfully", DATA_SV:"Lösenordet är nu ändrat"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Invalid request", DATA_SV:"Ogiltig förfrågan"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class VerifyUser(APIView):
    def get(self,request,uuid=None):
        try:
            print("hello")
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
        except:
            data = None
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if data:
                data.uuid = uuid4()
                data.is_active = True
                data.is_authenticated = True
                data.save()
                html_path = USER_WELCOME
                fullname = f'{data.first_name} {data.last_name}'
                context_data = {'fullname':fullname,}
                email_html_template = get_template(html_path).render(context_data)
                email_from = settings.EMAIL_HOST_USER
                recipient_list = (data.email_id,)
                email_msg = EmailMessage('Welcome To Eddi',email_html_template,email_from,recipient_list)
                email_msg.content_subtype = 'html'
                print("TRUE")
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
                return Response({STATUS: SUCCESS, DATA: "User verified successfully", DATA_SV:"Användaren är nu verifierad"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "User is not verified", DATA_SV:"Användaren kan inte verifieras"}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


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
                return Response({STATUS: SUCCESS, DATA: "Password changed successfully", DATA_SV:"Lösenordet är nu ändrat"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Invalid request", DATA_SV:"Ogiltig förfrågan"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class Header_FooterCMSDetails(APIView):
    def get(self, request):
        try:
            try:
                data = getattr(models,HEADER_FOOTERCMS_TABLE).objects.latest(CREATED_AT)
            except:
                data = None
            if not (serializer := Header_FooterCMSSerializer(data)):
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class Header_FooterCMSDetails_sv(APIView):
    def get(self, request):
        try:
            try:
                data = getattr(models,"Header_FooterCMS_SV").objects.latest(CREATED_AT)
            except:
                data = None
            if not (serializer := Header_FooterCMSSerializer_sv(data)):
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        except:
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
        except:
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
        except:
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
        except:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class GetHomePageDetails_sv(APIView):
    def get(self, request):
        try:
            try:
                data = getattr(models,"HomePageCMS_SV").objects.latest(CREATED_AT)
            except:
                data = None
            event_data = EventAd.objects.filter(Q(event_publish_on="Landing Page") | Q(event_publish_on="Both"))
            if not (serializer := HomePageCMSSerializer_sv(data)):
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            elif not (event_serializer := EventAdSerializer(event_data, many=True)):
                return Response({STATUS: ERROR, DATA: event_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({STATUS: SUCCESS, DATA: serializer.data, EVENT_DATA:event_serializer.data}, status=status.HTTP_200_OK)
        except:
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
        except:
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
        except:
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
        except:
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
        except:
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
            except:
                data = None
            if serializer := AboutUsCMSSerializer_sv(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass

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
            except:
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
        try:
            record_map = {
                FULLNAME : request.POST.get(FULLNAME),
                EMAIL_ID : request.POST.get(EMAIL_ID),
                PHONE_NUMBER : request.POST.get(PHONE_NUMBER),
                MESSAGE : request.POST.get(MESSAGE)
            }

            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[CREATED_BY] = request.POST.get(EMAIL_ID)
            try:
                getattr(models,CONTACT_FORM_TABLE).objects.update_or_create(**record_map)
            except Exception as e:
                print(e)
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Message sent successfully", DATA_SV:"Meddelandet är nu skickat"}, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class ContactFormView_sv(APIView):
    def post(self, request):
        try:
            record_map = {
                FULLNAME : request.POST.get(FULLNAME),
                EMAIL_ID : request.POST.get(EMAIL_ID),
                PHONE_NUMBER : request.POST.get(PHONE_NUMBER),
                MESSAGE : request.POST.get(MESSAGE)
            }

            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[CREATED_BY] = request.POST.get(EMAIL_ID)
            try:
                getattr(models,CONTACT_FORM_TABLE).objects.update_or_create(**record_map)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Message sent successfully", DATA_SV:"Meddelandet är nu skickat"}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    def post(self, request):
        email_id = get_user_email_by_token(request)
        user_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['usersignup_id'] = user_data.id
            try:
                if serializer.validated_data['agree_ads_terms'] == True:
                    try:
                        # user_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
                        message = f"{user_data.first_name}, has Agreed to view  “Recruitment Ad” "
                        message_sv = f"{user_data.first_name}, har accepterat rekryteringsannonsen"

                        data = getattr(models,USERSIGNUP_TABLE).objects.filter(user_type__user_type = "Admin")
                        receiver = [i.email_id for i in data]
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
                                record_map = {}
                                record_map = {
                                    "sender" : email_id,
                                    "receiver" : i,
                                    "message" : message,
                                    "message_sv" : message_sv
                                }
                                getattr(models,"Notification").objects.update_or_create(**record_map)
                            except:
                                pass
                    except:
                        pass
            except:
                pass
            serializer.save()
            return Response({STATUS: SUCCESS, DATA: "Profile created successfully", DATA_SV:"Profilen är nu skapad"}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
        except:
            data= None
        if serializer := UserProfileSerializer(data):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {
            PROFILE_IMAGE : request.FILES.get(PROFILE_IMAGE,data.profile_image),
            FIRST_NAME : request.POST.get(FIRST_NAME,data.first_name),
            LAST_NAME : request.POST.get(LAST_NAME,data.last_name),
            GENDER : request.POST.get(GENDER,data.gender),
            DOB : request.POST.get(DOB,data.dob),
            PERSONAL_NUMBER : request.POST.get(PERSONAL_NUMBER,data.personal_number),
            PHONE_NUMBER : request.POST.get(PHONE_NUMBER,data.phone_number),
            LOCATION : request.POST.get(USER_LOCATION,data.location),
            USER_INTERESTS : request.POST.get(USER_INTERESTS,data.user_interests),
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
            AREA_OF_INTEREST : request.POST.get(AREA_OF_INTEREST,data.area_of_interest)           
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
            return Response({STATUS: SUCCESS, DATA: "Profile updated successfully", DATA_SV:"Din profil är nu uppdaterad"}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            
            
@permission_classes([AllowAny])
class UserPaymentDetail_info(APIView):
    def post(self, request):
        try:
            course_name = request.POST.get(COURSE_NAME)
            course_data = getattr(models,COURSEDETAILS_TABLE).objects.get(**{"course_name":course_name})
            email_id = request.POST.get(EMAIL_ID)
            payment_mode = request.POST.get("payment_mode")
            user_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
            if request.POST.get(CARD_BRAND):
                card_type = request.POST.get(CARD_BRAND)
            else:
                card_type = None
            if request.POST.get(PRICE):
                amount = request.POST.get(PRICE)
                supplier_amount = request.POST.get('supplier_amount')
            else:
                amount = 0
                supplier_amount = 0

            if request.POST.get(STATUS):
                status_s = request.POST.get(STATUS)
            else:
                status_s = "Success"           
            record_map = {}
            record_map = {
                COURSE : course_data,
                EMAIL_ID: email_id,
                "user_name" : f"{user_data.first_name} {user_data.last_name}",
                CARD_TYPE : card_type,
                AMOUNT: float(amount),
                STATUS: status_s,
                CREATED_AT : make_aware(datetime.datetime.now()),
                "invoice" : getattr(models,"InvoiceData").objects.get(**{"course_name":course_data.course_name,"user_email":email_id})
                }

            if payment_mode == "eddi":
                record_map["payment_mode"] = "Eddi Platform"
                record_map[IS_APPROVED_ID] = 1
            elif payment_mode == "external":
                record_map["payment_mode"] = "External"
                record_map[IS_APPROVED_ID] = 2
            else:
                record_map["payment_mode"] = "Invoice"
                record_map[IS_APPROVED_ID] = 2

            try:
                var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, "course__course_name":course_name,STATUS:'Success'})
            except:
                var = None
            var = None
            if not var:
                try:
                    getattr(models,USER_PAYMENT_DETAIL).objects.update_or_create(**record_map)
                    profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:request.POST.get(EMAIL_ID)})
                    var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, COURSE:course_data,STATUS:'Success'})
                    courseobj = getattr(models,COURSEDETAILS_TABLE).objects.select_related('supplier').get(**{COURSE_NAME:course_name})
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
                        html_path = COURSE_ENROLL_HTML_TO_U
                        fullname = f"{user_data.first_name} {user_data.last_name}"
                        context_data = {'fullname':fullname, "email":user_data.email_id, "course_name":course_name}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (email_id,)
                        email_msg = EmailMessage('Congratulations!!',email_html_template,email_from,recipient_list)
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
                        supplier_data = getattr(models,'SupplierAccountDetail').objects.get(**{'supplier':course_data.supplier})
                        if supplier_data.total_earnings == None:
                            supplier_data.total_earnings = float(amount)
                        else:
                            supplier_data.total_earnings += float(amount)
                        supplier_data.save()
                    except Exception as ex:
                        print(ex)
                        pass
                    try:
                        sender_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{"email_id":email_id})
                    except:
                        pass
                    try:
                        message = f"{sender_data.first_name}, has Enrolled for the {courseobj.course_name} added by {courseobj.supplier.first_name}"
                        message_sv = f"{sender_data.first_name}, har registrerat sig på  {courseobj.course_name} added by {courseobj.supplier.first_name}"
                        receiver = [courseobj.supplier.email_id]
                        send_notification(email_id, receiver, message)
                        # receiver_device_token = []
                        # device_data = UserDeviceToken.objects.filter(user_type=courseobj.supplier)
                        # receiver_device_token.append(device_data.device_token)

                        # print(receiver_device_token)
                        # send_push_notification(receiver_device_token,message)
                        try:
                            record_map1 = {}
                            record_map1 = {
                                "sender" : email_id,
                                "receiver" : courseobj.supplier.email_id,
                                "message" : message,
                                "message_sv" : message_sv
                            }

                            getattr(models,"Notification").objects.update_or_create(**record_map1)
                        except:
                            pass
                    except:
                        pass
                    return Response({STATUS: SUCCESS, DATA: SUCCESS, DATA_SV:"Framgång"}, status=status.HTTP_200_OK)

                except Exception as e:
                    print(e)
                    return Response({MESSAGE: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({MESSAGE: ERROR, DATA: "You already enrolled", DATA_SV:"Du är redan registrerad"}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(e)
            return Response({STATUS:ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
                

@permission_classes([AllowAny])
class EventPaymentDetail_info(APIView):
    def post(self, request):
        user_email_id = get_user_email_by_token(request)
        try:
            event_name = request.POST.get(EVENT_NAME)
            event_data = getattr(models,EVENT_AD_TABLE).objects.get(**{"event_name":event_name})
            payment_mode = request.POST.get("payment_mode")
            user_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:user_email_id})
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
                "admin_name" : event_data.admin_name,
                "user_name" : user_data.first_name,
                EMAIL_ID: user_email_id,
                CARD_TYPE : card_type,
                AMOUNT: float(amount),
                STATUS: status_s,
                CREATED_AT : make_aware(datetime.datetime.now())
                }

            if payment_mode == "eddi":
                record_map["payment_mode"] = "Eddi Platform"
                record_map[IS_APPROVED_ID] = 1
            elif payment_mode == "external":
                record_map["payment_mode"] = "External"
                record_map[IS_APPROVED_ID] = 2
            else:
                record_map["payment_mode"] = "Invoice"
                record_map[IS_APPROVED_ID] = 2
            try:
                var = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.get(**{EMAIL_ID:user_email_id, EVENT_NAME:event_name,STATUS:SUCCESS})
            except:
                var = None
            if not var:
                try:
                    getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.update_or_create(**record_map)
                    profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:user_email_id})
                    var = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.get(**{EMAIL_ID:user_email_id, EVENT_NAME:event_name,STATUS:SUCCESS})
                    record_map = {}
                    record_map = {
                    EVENT_NAME : event_name,
                    USER_EMAIL : user_email_id,
                    PAYMENT_DETAIL_ID : var.id,
                    USER_PROFILE_ID : profile_data.id,
                    CREATED_AT : make_aware(datetime.datetime.now())
                    }
                    getattr(models,EVENTAD_ENROLL_TABLE).objects.update_or_create(**record_map)

                    try:
                        data_user = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:user_email_id})
                        message = f"{data_user.first_name}, has Registered for the “{event_name}” "
                        data = getattr(models,USERSIGNUP_TABLE).objects.filter(user_type__user_type = "Admin")
                        receiver = [i.email_id for i in data]
                        try:
                            translator= Translator(from_lang='english',to_lang="swedish")
                            message_sv = translator.translate(f"{data_user.first_name}, has Registered for the “{event_name}” ")
                        except:
                            pass
                        send_notification(user_email_id, receiver, message)
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
                                    "sender" : user_email_id,
                                    "receiver" : i,
                                    "message" : message,
                                    "message_sv" : message_sv
                                }
                                getattr(models,"Notification").objects.update_or_create(**record_map1)
                            except:
                                pass
                    except:
                        pass
                    return Response({STATUS: SUCCESS, DATA:"Information added successfully", DATA_SV:"Informationen har sparats"}, status=status.HTTP_200_OK)

                except:
                    return Response({MESSAGE: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({MESSAGE: ERROR, DATA: "You already enrolled", DATA_SV:"Du är redan registrerad"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({STATUS:ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


class FavCourseDetails(APIView):
    def post(self, request):
        email_id = get_user_email_by_token(request)
        record_map = {}
        try:
            course_name = request.POST.get(COURSE_NAME)
            fav_data = request.POST.get(IS_FAVOURITE)
        except:
            return Response({MESSAGE: ERROR, DATA: "We lack some information to perform this action", DATA_SV:"Data saknas för att avsluta detta"}, status=status.HTTP_400_BAD_REQUEST)
        
        if fav_data == 'true':
            record_map = {
            EMAIL_ID: email_id,
            COURSE_NAME : course_name,
            IS_FAVOURITE: json.loads(fav_data),
            CREATED_AT : make_aware(datetime.datetime.now())
            }
            try:
                data = getattr(models,FAVOURITE_COURSE_TABLE).objects.get(**{EMAIL_ID:email_id,COURSE_NAME:course_name})
            except:
                data = None
            if data == None:
                try:
                    getattr(models,FAVOURITE_COURSE_TABLE).objects.update_or_create(**record_map)
                    return Response({MESSAGE: SUCCESS, DATA:"Information added successfully", DATA_SV:"Informationen har sparats"}, status=status.HTTP_200_OK)
                except:
                    return Response({MESSAGE: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({MESSAGE: ERROR, DATA: "Selected course is already marked as a favourite", DATA_SV:"Vald utbildning är redan markerad som en favorit"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user_data_fav = getattr(models,FAVOURITE_COURSE_TABLE).objects.get(**{EMAIL_ID:email_id,COURSE_NAME:course_name})
            except:
                return Response({MESSAGE: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            user_data_fav.delete()
            return Response({MESSAGE: SUCCESS, DATA: "Data removed from your favourite listing", DATA_SV:"Detta innehåll har flyttats från dina favoriter"}, status=status.HTTP_200_OK)
            
    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            if getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type =='User':
                try:
                    data = getattr(models,FAVOURITE_COURSE_TABLE).objects.filter(**{EMAIL_ID:email_id}).values_list("course_name", flat = True).order_by("-created_date_time")
                except:
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
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


class ViewIndividualProfile(APIView):
    def post(self, request):
        email_id = get_user_email_by_token(request)
        user_email_id = request.POST.get(EMAIL_ID)
        supplier_email_id = request.POST.get(SUPPLIER_EMAIL_ID)
        token_data = request.headers.get('Authorization')
        try:
            token = token_data.split()[1]   
            data = getattr(models,TOKEN_TABLE).objects.get(key = token)
        except:
            return Response({MESSAGE: ERROR, DATA: "Token Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course_list = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__email_id":user_email_id, SUPPLIER_EMAIL:supplier_email_id})
        except:
            return Response({STATUS: ERROR, DATA: "Course list Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:user_email_id})          
            if serializer := UserProfileSerializer(profile_data):
                if serializer1 := CourseEnrollSerializer(course_list, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data, "Course":serializer1.data, "Ongoing_Course":course_list.count()}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class IncreaseAdCount(APIView):
    def put(self, request, uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,EVENT_AD_TABLE).objects.get(**{UUID:uuid})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({STATUS: SUCCESS, DATA:"Information added successfully", DATA_SV:"Informationen har sparats"}, status=status.HTTP_200_OK)

class IncreaserecruitmentAdCount(APIView):
    def put(self, request, uuid = None):
        email_id = get_user_email_by_token(request)
        try:
            user_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,"RecruitmentAd").objects.get(**{UUID:uuid})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({STATUS: SUCCESS, DATA: "Subscriber count increased successfully", DATA_SV:"Användarregistrering har nu uppdaterats"}, status=status.HTTP_200_OK)
        

class EventView(APIView):
    def post(self, request):
        email_id = get_user_email_by_token(request)
        admin = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}) 
        record_map = {}

        if request.POST.get(EVENT_NAME):
            try:
                event_data = getattr(models,EVENT_AD_TABLE).objects.get(**{"event_name":request.POST.get(EVENT_NAME)})
            except:
                event_data = None
            if event_data != None:
                return Response({STATUS: ERROR, DATA:"Please choose unique event name", DATA_SV:"Vänligen välj ett specifikt namn på eventet"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {
            "admin_name" : f"{admin.first_name} {admin.last_name}",
            "admin_email" : email_id,
            EVENT_IMAGE : request.FILES.get(EVENT_IMAGE,None),
            EVENT_PUBLISH_ON : request.POST.get(EVENT_PUBLISH_ON,None),
            EVENT_NAME : request.POST.get(EVENT_NAME,None),
            EVENT_CATEGORY : request.POST.get(EVENT_CATEGORY,None),
            EVENT_CHOOSE_TYPE : request.POST.get(EVENT_CHOOSE_TYPE,None),
            BANNER_VIDEO_LINK : request.POST.get(BANNER_VIDEO_LINK,None),
            FEES_TYPE : request.POST.get(FEES_TYPE,None),
            EVENT_TYPE : request.POST.get(EVENT_TYPE,None),
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
            if request.POST.get(EVENT_PRICE):
                record_map[EVENT_PRICE] = "{:.2f}".format(float(request.POST.get(EVENT_PRICE)))
            if request.POST.get(ORIGINAL_PRICE):
                record_map[ORIGINAL_PRICE] = "{:.2f}".format(float(request.POST.get(ORIGINAL_PRICE)))
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
            return Response({STATUS: SUCCESS, DATA:"Information added successfully", DATA_SV:"Informationen har sparats"}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, uuid = None):
        email_id = get_user_email_by_token(request)
        try:
            vat = getattr(models,"InvoiceVATCMS").objects.all().values_list("vat_value", flat=True)
            vat_val = int(vat[0])
        except:
            vat_val = None
        if uuid:
            data = getattr(models,EVENT_AD_TABLE).objects.get(**{UUID:uuid})
            user_email = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.filter(**{EVENT_NAME:data.event_name}).values_list('email_id', flat=True)
            print(user_email,"eeeeeeeeeeeee")
            subscriber = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.filter(**{EVENT_NAME:data.event_name, "status":"Success"}).count()
            individuals = getattr(models,USER_PROFILE_TABLE).objects.filter(**{"email_id__in":user_email})
            print(individuals, "indididi")

            try:
                var = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.get(**{EMAIL_ID:email_id, EVENT_NAME:data.event_name,STATUS:SUCCESS})
            except:
                var = None
            var1 = True if var is not None else False
            if serializer := EventAdSerializer(data):
                if serializer2 := UserProfileSerializer(individuals, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data, SUBSCRIBER_COUNT:subscriber, "is_enrolled":var1, "VAT_charges":vat_val, "individuals":serializer2.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer2.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == ADMIN_S:
                try:
                    data_a = getattr(models,EVENT_AD_TABLE).objects.filter(**{IS_DELETED:False}).order_by("-created_date_time")
                except:
                    return Response({STATUS: ERROR, DATA:"Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
                if serializer := EventAdSerializer(data_a,many=True):
                        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                try:
                    cat = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                    a = cat.course_category.split(",")
                except:
                    a = cat.course_category.split()
                user_data = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.filter(**{EMAIL_ID:email_id}).values_list("event_name", flat=True)
                category_event = getattr(models,EVENT_AD_TABLE).objects.filter(**{STATUS_ID:1,IS_DELETED:False}).filter(Q(event_name__in = a) | Q(event_category__in = a)).exclude(event_name__in = user_data).order_by("-created_date_time")

                category_event_data = getattr(models,EVENT_AD_TABLE).objects.filter(**{STATUS_ID:1,IS_DELETED:False}).filter(Q(event_name__in = a) | Q(event_category__in = a)).exclude(event_name__in = user_data).values_list(EVENT_NAME, flat=True)

                all_event_data = getattr(models,EVENT_AD_TABLE).objects.filter(**{STATUS_ID:1,IS_DELETED:False}).order_by("-created_date_time")
                if serializer := EventAdSerializer(all_event_data, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self, request, uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,EVENT_AD_TABLE).objects.get(**{UUID:uuid})   
                     
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            enrolled = getattr(models,EVENTAD_PAYMENT_DETAIL_TABLE).objects.filter(**{EVENT_NAME:data.event_name})
            if enrolled.exists():
                return Response({STATUS: ERROR, DATA: "Someone already enrolled in this event you can't edit", DATA_SV:"Någon är redan anmäld till eventet, innehållet kan inte redigeras"}, status=status.HTTP_400_BAD_REQUEST)
        except:
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
            CHECKOUT_LINK : request.POST.get(CHECKOUT_LINK,data.checkout_link),
            MEETING_LINK : request.POST.get(MEETING_LINK,data.meeting_link),
            MEETING_PASSCODE : request.POST.get(MEETING_PASSCODE,data.meeting_passcode),
            EVENT_SMALL_DESCRIPTION : request.POST.get(EVENT_SMALL_DESCRIPTION,data.event_small_description),
            EVENT_DESCRIPTION : request.POST.get(EVENT_DESCRIPTION,data.event_description),
            EVENT_LOCATION: request.POST.get(EVENT_LOCATION,data.event_location),
            EVENT_ORGANIZER : request.POST.get(EVENT_ORGANIZER,data.event_organizer),
            EVENT_SUBSCRIBER : request.POST.get(EVENT_SUBSCRIBER,data.event_subscriber),
            
            }
            if request.POST.get(EVENT_PRICE):
                record_map[EVENT_PRICE] = "{:.2f}".format(float(request.POST.get(EVENT_PRICE)))
            else:
                 record_map[EVENT_PRICE] = data.event_price
            if request.POST.get(ORIGINAL_PRICE):
                record_map[ORIGINAL_PRICE] = "{:.2f}".format(float(request.POST.get(ORIGINAL_PRICE)))
            else:
                record_map[ORIGINAL_PRICE] = data.original_price
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
                    except:
                        dataa = None
                    if dataa.exists():
                        return Response({STATUS: ERROR, DATA: "Someone already enrolled in this event you can't edit", DATA_SV:"Någon är redan anmäld till eventet, innehållet kan inte redigeras"}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response({STATUS: SUCCESS, DATA: "Information successfully edited", DATA_SV:"Din information har nu ändrats"}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: ERROR}, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self,request,uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,EVENT_AD_TABLE).objects.get(**{UUID:uuid})
        except:
            return Response({STATUS: ERROR, DATA:"Data not found", DATA_SV:"Ingen information tillgänglig"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {}
            record_map[STATUS_ID] = 2
            record_map[IS_DELETED] = True
            record_map[UUID] = uuid4()
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()
            return Response({STATUS: SUCCESS, DATA: "Information succesfully deleted", DATA_SV:"Data har nu raderats"}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong in deleting data", DATA_SV:"Något gick fel när data skulle raderas"}, status=status.HTTP_200_OK)


class RecruitmentAdView(APIView):
    def post(self, request):
        email_id =  get_user_email_by_token(request)
        record_map = {}
        try:
            supplier_id = getattr(models,"SupplierProfile").objects.get(**{"supplier_email":email_id})
        except:
            return Response({STATUS: ERROR, DATA: "You need to add a supplier profile first", DATA_SV:"Leverantörsprofil måste först läggas till"}, status=status.HTTP_200_OK)
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
            try:
                data_supplier = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id})
                message = f"{data_supplier.first_name}, has added a new Recruitment Ad“{request.POST.get(RECRUITMENTAD_TITLE)}” to the system"
                data = getattr(models,USERSIGNUP_TABLE).objects.filter(user_type__user_type = "Admin")
                receiver = [i.email_id for i in data]
                title = request.POST.get(RECRUITMENTAD_TITLE)
                try:
                    translator= Translator(from_lang='english',to_lang="swedish")
                    message_sv = translator.translate(f"{data_supplier.first_name}, has added a new Recruitment Ad“{title}” to the system")
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
            return Response({STATUS: SUCCESS, DATA: "Information successfully added", DATA_SV:"Informationen har nu sparats"}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)


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
                data = getattr(models,RECRUITMENTAD_TABLE).objects.filter(**{"recruitmentAd_Expiry__gte":datetime.datetime.now().date(), IS_DELETED:False}).order_by("-created_date_time")
                if serializer := RecruitmentAdSerializer(data, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            elif getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == ADMIN_S:
                data = getattr(models,RECRUITMENTAD_TABLE).objects.filter(**{IS_DELETED:False}).order_by("-created_date_time")
                if serializer := RecruitmentAdSerializer(data, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            elif getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type == SUPPLIER_S:
                try:
                    data = getattr(models,RECRUITMENTAD_TABLE).objects.filter(**{"supplier_profile__supplier_email":email_id, IS_DELETED:False}).order_by("-created_date_time")
                except:
                    return Response({STATUS: ERROR, DATA: "You have not added recruitment ads yet"}, status=status.HTTP_400_BAD_REQUEST)
                if serializer := RecruitmentAdSerializer(data, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({STATUS: ERROR, DATA:"You have not agreed to get recruitment ads", DATA_SV:"Du har inte lagt till någon rekryteringsannons ännu"}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, uuid = None):
        email_id =  get_user_email_by_token(request)
        try:
            user_type_data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id}).user_type.user_type
        except Exception:
            user_type_data = None
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,RECRUITMENTAD_TABLE).objects.get(**{UUID:uuid})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

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
                            try:
                                message = f"{record_map[RECRUITMENTAD_TITLE]}, has been Approved by the Admin"
                                message_sv = f"Rekryteringsannonsen {record_map[RECRUITMENTAD_TITLE]} har godkänts av Eddi Admin"
                                receiver = [data.supplier_profile.supplier_email]
                                title = record_map[RECRUITMENTAD_TITLE]
                                send_notification(email_id, receiver, message)
                                # receiver_device_token = []
                                # for i in data:
                                #     device_data = UserDeviceToken.objects.filter(user_type=i)
                                #     for j in device_data:
                                #         receiver_device_token.append(j.device_token)
                                # print(receiver_device_token)
                                # send_push_notification(receiver_device_token)
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
                        elif request.POST.get(APPROVAL_STATUS) == "Pending":
                            record_map[IS_APPROVED_ID] = 2
                        else:
                            record_map[IS_APPROVED_ID] = 3
                            try:
                                message = f"{record_map[RECRUITMENTAD_TITLE]}, has been Rejected by the Admin"
                                message_sv = f"Rekryteringsannonsen {record_map[RECRUITMENTAD_TITLE]}, har inte godkänts av Eddi Admin"
                                receiver = [data.supplier_profile.supplier_email]
                                title = record_map[RECRUITMENTAD_TITLE]
                                send_notification(email_id, receiver, message)
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
                            record_map[STATUS_ID] = 2
                    else:
                        record_map[STATUS] = data.status
                        record_map[IS_APPROVED_ID] = 2

            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[UUID] = uuid4()
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()            
            return Response({STATUS: SUCCESS, DATA: "Information successfully edited", DATA_SV:"Din information har nu ändrats"}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self,request,uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,RECRUITMENTAD_TABLE).objects.get(**{UUID:uuid})
        except:
            return Response({STATUS: ERROR, DATA:"Data not found", DATA_SV:"Ingen information tillgänglig"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {}
            record_map[STATUS_ID] = 2
            record_map[IS_DELETED] = True
            record_map[UUID] = uuid4()
            for key,value in record_map.items():
                setattr(data,key,value)
            data.save()
            return Response({STATUS: SUCCESS, DATA: "Information succesfully deleted", DATA_SV:"Data har nu raderats"}, status=status.HTTP_200_OK)
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong in deleting data", DATA_SV:"Något gick fel när data skulle raderas"}, status=status.HTTP_200_OK)



# For My Course Page
class CourseEnrollView(APIView):
    def post(self, request):
        email_id =  get_user_email_by_token(request)
        var = request.POST.get("filter")
        try:
            enroll_data = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{'email_id':email_id,IS_APPROVED_ID:1}).order_by("-created_date_time")
        except:
            enroll_data = None

        if var == "all":
            new_dict = OrderedDict()
            try:
                for i in enroll_data: 
                    view_material = False
                    try:
                        var = getattr(models,"CourseMaterial").objects.get(**{'course__uuid':i.course.uuid})
                        all_videos = var.video_files.all()
                        view_material = True
                    except:
                        var = None
                        new_dict[f"course_{i}"] = f"Ongoing {view_material}"
                        continue
                    l1 = []
                    for j in all_videos:
                        try:
                            material_status = getattr(models,"CourseMaterialStatus").objects.get(**{'user_email':email_id, 'video_id':j.uuid})
                            l1.append(material_status.is_complete)
                        except:
                            pass
                    if len(l1) != len(all_videos) or False in l1:
                        new_dict[f"course_{i}"] = f"Ongoing {view_material}"
                    else:
                        new_dict[f"course_{i}"] = f"Completed {view_material}"                          
            except:
                pass
        elif var == "ongoing":
            new_dict = OrderedDict()
            try:
                ongoing_coures_uuid = []
                for i in enroll_data: 
                    view_material = False
                    try:
                        var = getattr(models,"CourseMaterial").objects.get(**{'course__uuid':i.course.uuid})
                        print(var,"vararar")
                        all_videos = var.video_files.all()
                        view_material = True
                    except:
                        var = None
                        print(i,"ii")
                        new_dict[f"course_{i}"] = f"Ongoing {view_material}"
                        print(new_dict,"neww")
                        ongoing_coures_uuid.append(i)
                        continue
                    l1 = []
                    for j in all_videos:
                        try:
                            material_status = getattr(models,"CourseMaterialStatus").objects.get(**{'user_email':email_id, 'video_id':j.uuid})
                            l1.append(material_status.is_complete)
                        except:
                            material_status = None
                    if len(l1) != len(all_videos) or False in l1:
                        print(i,"iii")
                        new_dict[f"course_{i}"] = f"Ongoing {view_material}"
                        print(new_dict,"new")
                        ongoing_coures_uuid.append(i)
                print(ongoing_coures_uuid, "ongoingggg")
                enroll_data = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{'course__course_name__in':ongoing_coures_uuid, EMAIL_ID:email_id}).order_by("-created_date_time")
            except:
                enroll_data = None

        elif var == "completed":
            new_dict = OrderedDict()
            try:
                completed_coures_uuid = []
                print(enroll_data, "enrolldatatat")
                for i in enroll_data: 
                    view_material = False
                    try:
                        var = getattr(models,"CourseMaterial").objects.get(**{'course__uuid':i.course.uuid})
                        all_videos = var.video_files.all()
                        view_material = True
                    except:
                        var = None
                        continue
                    l1 = []
                    for j in all_videos:
                        try:
                            material_status = getattr(models,"CourseMaterialStatus").objects.get(**{'user_email':email_id, 'video_id':j.uuid})
                            l1.append(material_status.is_complete)
                            print(material_status.is_complete, "okok")
                        except:
                            material_status = None
                    if len(l1) == len(all_videos) and False not in l1:
                        print("inside lenenene")
                        new_dict[f"course_{i}"] = f"Completed {view_material}"
                        completed_coures_uuid.append(i)
                print(completed_coures_uuid, "uuiddidid")
                enroll_data = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{'course__course_name__in':completed_coures_uuid, EMAIL_ID:email_id}).order_by("-created_date_time")
            except:
                enroll_data = None
                
        try:
            cat = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
            try:
                area_of_interest = cat.area_of_interest.split(",")
            except:
                area_of_interest = cat.area_of_interest.split()
            try:
                a = cat.course_category.split(",")
            except:
                a = cat.course_category.split()
        except:
            pass
        organization_domain = email_id.split('@')[1]
        try:
            data_category = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False, COURSE_FOR_ORGANIZATION:False}).filter(Q(course_category__category_name__in = area_of_interest) | Q(course_name__in = area_of_interest)).exclude(course_name__in=enroll_data).order_by("-organization_domain")
        except:
            data_category = None
        if serializer := UserPaymentSerializer(enroll_data, many=True):
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
            except:
                enroll_data = None

            try:
                event_data = getattr(models,EVENT_AD_TABLE).objects.filter(**{'event_name__in':list(enroll_data)}).order_by("-created_date_time")
            except:
                event_data = None

            try:
                category = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                
                a = category.course_category.split(",")
            except:
                try:
                    a = category.course_category.split()
                except:
                    a = None
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
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)



class CourseMaterialStatus(APIView):
    def post(self, request):
        email_id =  get_user_email_by_token(request)
        video_id = request.POST.get("video_id")
        try:
            try:
                data = getattr(models,"CourseMaterialStatus").objects.get(**{'user_email':email_id, "video_id":video_id})
            except:
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
        except:
            pass
        return Response({STATUS: SUCCESS, DATA: "Material status added successfully", DATA_SV:"Utbildningsunderlag har nu lagts till"}, status=status.HTTP_200_OK)


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
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,"CourseRating").objects.get(**{"user":user, "course_name":course})
        except:
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

            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                getattr(models,"CourseRating").objects.update_or_create(**record_map)
                try:
                    admin_email = getattr(models,USERSIGNUP_TABLE).objects.get(**{"user_type__user_type":"Admin"})
                except:
                    pass
                if course.created_by == "Admin":
                    try:
                        html_path = "user_rate_to_admin.html"
                        fullname = f'{user.first_name} {user.last_name}'
                        context_data = {'supplier_name':course.supplier.first_name,'fullname':fullname,"course_name":course.course_name,'star':"{:.1f}".format(int(request.POST.get("star"))),"review":request.POST.get("comment")}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (admin_email.email_id,)
                        email_msg = EmailMessage('Someone has Rated your Course',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        print("TRUE")
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
                        print("TRUE")
                    except:
                        pass
                else:
                    try:
                        html_path = "user_rate_to_supplier.html"
                        fullname = f'{user.first_name} {user.last_name}'
                        context_data = {'supplier_name':course.supplier.first_name,'fullname':fullname,"course_name":course.course_name,'star':"{:.1f}".format(int(request.POST.get("star"))),"review":request.POST.get("comment")}
                        email_html_template = get_template(html_path).render(context_data)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = (admin_email.email_id,)
                        email_msg = EmailMessage('Someone has Rated your Course',email_html_template,email_from,recipient_list)
                        email_msg.content_subtype = 'html'
                        print("TRUE")
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
                        print("TRUE")
                    except:
                        pass

                return Response({STATUS: SUCCESS, DATA:"Information added successfully", DATA_SV:"Informationen har sparats"}, status=status.HTTP_200_OK)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({STATUS: SUCCESS, DATA: "Information successfully edited", DATA_SV:"Din information har nu ändrats"}, status=status.HTTP_200_OK)
            except:
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, uuid=None):
        email_id = get_user_email_by_token(request)
        try:
            user = getattr(models,USER_PROFILE_TABLE).objects.get(**{"email_id":email_id})
            course = getattr(models,COURSEDETAILS_TABLE).objects.get(**{"uuid":uuid})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = getattr(models,"CourseRating").objects.get(**{"user":user, "course_name":course})
        except:
            return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer := CourseRatingSerializer(data):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        return Response({STATUS: SUCCESS, DATA: serializer.error}, status=status.HTTP_200_OK)


class Notification(APIView):
    def put(self, request):
        email_id = get_user_email_by_token(request)
        is_clear = json.loads(request.POST.get("is_clear"))
        if request.POST.get("is_clear"):
            try:
                data = getattr(models,"Notification").objects.filter(**{"receiver__icontains":email_id})
                for i in data:
                    i.is_clear = True
                    i.save()
                return Response({STATUS: SUCCESS, DATA: "Notification Cleared"}, status=status.HTTP_200_OK)
            except:
                return Response({STATUS: SUCCESS, DATA: "Something went wrong"}, status=status.HTTP_200_OK)
    
    def get(self, request):
        email_id = get_user_email_by_token(request)
        try:
            data = getattr(models,"Notification").objects.filter(**{"receiver__icontains":email_id, "is_clear":False}).order_by("-created_date_time")
        except:
            data = None
        if serializer := NotificationSerializer(data, many=True):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        return Response({STATUS: SUCCESS, DATA: serializer.error}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class User_Profile_CMS(APIView):
    def get(self,request):
        try:
            data = getattr(models,"UserProfileCMS").objects.all()
        except:
            data = None
        if serializer := UserProfileCMSSerializer(data, many=True):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        return Response({STATUS: SUCCESS, DATA: serializer.error}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class User_Profile_CMS_sv(APIView):
    def get(self,request):
        try:
            data = getattr(models,"UserProfileCMS_SV").objects.all()
        except:
            data = None
        if serializer := UserProfileCMS_SVSerializer(data, many=True):
            return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        return Response({STATUS: SUCCESS, DATA: serializer.error}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class AllSubCategory(APIView):
    def get(self, request):
        try:
            all_subcategory = getattr(models,COURSE_SUBCATEGORY_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1, IS_DELETED:False})
        except:
            all_subcategory = None
        try:
            if all_subcategory_serializer := SubCategoryDetailsSerializer(all_subcategory, many=True):
                return Response({STATUS: SUCCESS,
                ALL_SUBCATEGORY: all_subcategory_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: SUCCESS, DATA: all_subcategory_serializer.error}, status=status.HTTP_200_OK)
        except:
            pass



class Manage_Payment(APIView):
    def get(self, request):
        email_id = get_user_email_by_token(request)
        data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
        if data.user_type.user_type == ADMIN_S:
            try:
                all_payment = getattr(models,"UserPaymentDetail").objects.all().order_by("-created_date_time")
            except:
                all_payment = None
            try:
                all_event = getattr(models,"EventAdPaymentDetail").objects.all().order_by("-created_date_time")
            except:
                all_event = None
            try:
                if serializer := UserPaymentSerializer(all_payment, many=True):
                    if serializer1 := EventAdPaymentDetailSerializer(all_event, many=True):
                        return Response({STATUS: SUCCESS, DATA: serializer.data, "event":serializer1.data}, status=status.HTTP_200_OK)
                    else:
                        return Response({STATUS: SUCCESS, DATA: serializer1.error}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: SUCCESS, DATA: serializer.error}, status=status.HTTP_200_OK)
            except:
                pass
        elif data.user_type.user_type == SUPPLIER_S:
            try:
                all_payment = getattr(models,"UserPaymentDetail").objects.filter(**{"course__supplier__email_id":email_id})
            except:
                all_payment = None
            try:
                supplier_account_data = getattr(models,"SupplierAccountDetail").objects.get(**{"supplier__email_id":email_id})
            except:
                pass
            try:
                if serializer := UserPaymentSerializer(all_payment, many=True):
                    if serializer1 := SupplierAccountDetailSerializer(supplier_account_data):
                        return Response({STATUS: SUCCESS, DATA: serializer.data, 'supplier_account_data':serializer1.data}, status=status.HTTP_200_OK)
                    else:
                        return Response({STATUS: SUCCESS, DATA: serializer1.error}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: SUCCESS, DATA: serializer.error}, status=status.HTTP_200_OK)
            except:
                pass

    def put(self, request, uuid=None):
        email_id = get_user_email_by_token(request)
        # approval_status = request.POST.get(APPROVAL_STATUS)
        data = getattr(models,USERSIGNUP_TABLE).objects.select_related('user_type').get(**{EMAIL_ID:email_id})
        if not uuid:
            return Response({STATUS: SUCCESS, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_200_OK)
        if data.user_type.user_type == SUPPLIER_S or data.user_type.user_type == ADMIN_S:
            print("admininin")
            try:
                try:
                    payment_data = getattr(models,"UserPaymentDetail").objects.get(**{UUID:uuid})
                except:
                    payment_data = None

                record_map = {}
                if request.POST.get(APPROVAL_STATUS) == "Approved":
                    record_map[IS_APPROVED_ID] = 1
                    record_map["status"] = "Success"
                elif request.POST.get(APPROVAL_STATUS) == "Pending":
                    record_map[IS_APPROVED_ID] = 2
                else:
                    record_map[IS_APPROVED_ID] = 3

                for key, value in record_map.items():
                    setattr(payment_data, key, value)
                payment_data.save()
                return Response({STATUS: SUCCESS, DATA:"Payment status changed successfully", DATA_SV:"Betalningsstatus har nu ändrats"}, status=status.HTTP_200_OK)
            except:
                return Response({STATUS: SUCCESS, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: SUCCESS, DATA: "You are not authorized to do this", DATA_SV:"Du har inte behörighet att utföra detta"}, status=status.HTTP_400_BAD_REQUEST)


class GetUserSessionView(APIView):
    def get(self, request):
        try:
            email_id = get_user_email_by_token(request)
            try:
                user_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
            except Exception as e:
                print(e)
                return Response({STATUS: ERROR, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_400_BAD_REQUEST)
            batch_detail = getattr(models,COURSE_BATCH).objects.filter(**{"students__in":[user_data]})
            all_session = []
            
            for batch in batch_detail:
                sessions = getattr(models,BATCH_SESSION).objects.filter(**{BATCH:batch})
                all_session.extend(sessions)

            try:
                if serializer := SessionDetailsSerializer(all_session, many=True):
                    return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({STATUS: SUCCESS, DATA: serializer.error}, status=status.HTTP_200_OK)
            except:
                pass
            
        except Exception as e:
            print(e)
            return Response({STATUS: SUCCESS, DATA: "Something went wrong please try again", DATA_SV:"Något gick fel försök igen"}, status=status.HTTP_200_OK)