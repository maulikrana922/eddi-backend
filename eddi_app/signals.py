from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from email.mime.image import MIMEImage
import os
from .models import CourseDetails,UserSignup,Notification,SupplierProfile,ContactFormLead,ContactFormLead_SV,SupplierAccountDetail,UserDeviceToken,BatchSession
from django.core import mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .notification import  send_push_notification
from django.template.loader import get_template
from eddi_app.constants.constants import *
from eddi_app.constants.table_name import *
from django.contrib.auth.hashers import make_password
import random
import string
from translate import Translator

otp = ''


# Create your models here.
def PasswordView():
    global otp
    context = None
    digits = f"{str(string.ascii_letters)}{str(string.digits)}!@#$%^&*()"
    otp = "".join(random.choices(digits, k=6))
    print(otp)
    return otp

@receiver(post_save, sender=CourseDetails)
def add_organization_domain(sender, instance, created, **kwargs):
    if created and instance.course_for_organization == True:
        try:
            test_str = instance.supplier.email_id
            res = test_str.split('@')[1]
            # print(res)
            CourseDetails.objects.filter(uuid = instance.uuid).update(organization_domain = str(res))
        except Exception as e:
            print(e,"essssss")

@receiver(post_save, sender=CourseDetails)
def bulk_email(sender, instance, created, **kwargs):
    if instance.course_for_organization == True and instance.is_post == True:
        connection = mail.get_connection()
        if instance.target_users != None:
            try:
                reciever_list = instance.target_users.split(",")
            except Exception as ex:
                reciever_list = instance.target_users.split()
        else:
            reciever_list = []
        try:
            path = 'eddi_app'
            img_dir = 'static'
            image = 'Logo.png'
            file_path = os.path.join(path,img_dir,image)
            with open(file_path,'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<{name}>'.format(name=image))
                img.add_header('Content-Disposition', 'inline', filename=image)
            html_path = 'target_users_organization.html'
            connection.open()
            email_from = settings.EMAIL_HOST_USER
            for i in reciever_list:
                try:
                    user_detail = UserSignup.objects.get(email_id = i)
                    if user_detail.is_swedishdefault:
                        subject = 'Inbjudan från Eddi - En utbildning för dig'
                    else:
                        subject = 'Invite to a new course'
                    username = user_detail.first_name
                except Exception as ex:
                    username = None
                try:
                    organization_data = instance.supplier_organization.organizational_name
                except Exception as ex:
                    print(ex,"exxx")
                    organization_data = None
                context_data = {'course_name':instance.course_name, "user_name" : username, "supplier_name" : instance.supplier.first_name, "organization_name" : organization_data, "url":FRONT_URL+f"view-course-details/{instance.uuid}/","swedish_default":user_detail.is_swedishdefault}
                html_content = render_to_string(html_path, context_data)               
                text_content = "..."                      
                receiver = i,
                msg = EmailMultiAlternatives(subject, text_content, email_from, receiver, connection=connection)                                      
                msg.attach_alternative(html_content, "text/html")
                msg.attach(img)
                msg.send()
            connection.close()
            instance.is_post = False
            instance.save()
        except Exception as ex:
            print(ex,"exx")
            pass

@receiver(post_save, sender=ContactFormLead)
@receiver(post_save, sender=ContactFormLead_SV)
def send_contactlead_email(sender, instance, created, **kwargs):
    if created:
        html_path = CONTACT_LEAD
        # if instance.is_swedishdefault:
        subject = 'Förfrågan från användare'
        # else:
        #     subject = 'General inquiry from ser'
        context_data = {'fullname':instance.fullname, "email":instance.email_id, "phone":instance.phone_number, "msg":instance.message,"swedish_default":True}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ('jap.admin@yopmail.com',)
        email_msg = EmailMessage(subject,email_html_template,email_from,recipient_list)
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


@receiver(post_save, sender=ContactFormLead)
@receiver(post_save, sender=ContactFormLead_SV)
def send_contact_usl(sender, instance, created, **kwargs):
    if created:
        html_path = CONTACTUS_USER
        # if instance.is_swedishdefault:
        subject = 'Förfrågan har skickats till Eddi'
        # else:
        #     subject = 'Inquiry submitted'
        context_data = {'fullname':instance.fullname,"swedish_default":True}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
        email_msg = EmailMessage(subject,email_html_template,email_from,recipient_list)
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

@receiver(post_save, sender=UserSignup)
def send_appointment_confirmation_email(sender, instance, created, **kwargs):
    print("OUTER")
    if created and instance.user_type.user_type == ADMIN_S:
        try:
            record_map = {}
            record_map = {
                "supplier_name" : f"{instance.first_name} {instance.last_name}",
                "supplier_email" : f"{instance.email_id}"
            }
            SupplierProfile.objects.update_or_create(**record_map)
        except Exception as ex:
            print(ex, "exexexexe")
        html_path = OTP_EMAIL_HTML
        otp = PasswordView()
        fullname = f'{instance.first_name} {instance.last_name}'
        if instance.is_swedishdefault:
            subject = 'Välkommen till Eddi!'
        else:
            subject = 'Welcome to the Eddi Platform!'
            
        context_data = {'final_otp':otp,'fullname':fullname, "email":instance.email_id,"url":SUPPLIER_URL,"swedish_default":instance.is_swedishdefault,"user_type":'Admin',}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
        data = UserSignup.objects.get(email_id = instance.email_id)
        data.password = make_password(otp)
        data.save()
        record_map = {
            'supplier' : data,
        }
        SupplierAccountDetail.objects.update_or_create(**record_map)
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

    if created and instance.user_type.user_type == SUPPLIER_S:
        try:
            message = f"{instance.first_name}, as a Supplier has been added by the System."
            # send_notification(sender, receiver, message, sender_type=None, receiver_type=None)
            data = UserSignup.objects.filter(user_type__user_type = "Admin")
            receiver = [i.email_id for i in data]
            receiver_device_token = []
            for i in data:
                device_data = UserDeviceToken.objects.filter(user_type=i)
                for j in device_data:
                    receiver_device_token.append(j.device_token)

            try:
                translator= Translator(from_lang='english',to_lang="swedish")
                message_sv = translator.translate(f"{instance.first_name}, as a Supplier has been added by the System.")
            except:
                pass
            # send_notification(instance.email_id, receiver, message)
            send_push_notification(receiver_device_token,message)
            for i in receiver:
                try:
                    record_map1 = {}
                    record_map1 = {
                        "sender" : instance.email_id,
                        "receiver" : i,
                        "message" : message,
                        "message_sv" : message_sv,
                    }

                    Notification.objects.update_or_create(**record_map1)
                except Exception as ex:
                    print(ex,"exexe")
                    pass
        except:
            pass
        try:
            record_map = {}
            record_map = {
                "supplier_name" : f"{instance.first_name} {instance.last_name}",
                "supplier_email" : f"{instance.email_id}"
            }
            SupplierProfile.objects.update_or_create(**record_map)
        except Exception as ex:
            print(ex, "exexexexe")

        html_path = OTP_EMAIL_HTML
        otp = PasswordView()
        fullname = f'{instance.first_name} {instance.last_name}'
        if instance.is_swedishdefault:
            subject = 'Välkommen till Eddi!'
            user_type = 'leverantör'
        else:
            subject = 'Welcome to the Eddi Platform!'
            user_type = 'Supplier'
        context_data = {'final_otp':otp,'fullname':fullname, "email":instance.email_id,"swedish_default":instance.is_swedishdefault,"url":SUPPLIER_URL,"user_type":user_type}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
        data = UserSignup.objects.get(email_id = instance.email_id)
        data.password = make_password(otp)
        data.save() 
        email_msg = EmailMessage(subject,email_html_template,email_from,recipient_list)
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

    if created and instance.user_type.user_type == 'User':
        print("insideeeee")
        html_path = VERIFY_EMAIL
        fullname = f'{instance.first_name} {instance.last_name}'
        if instance.is_swedishdefault:
            subject = 'Vänligen verifiera ditt konto hos Eddi'
        else:
            subject = 'Please verify your Eddi account'
        context_data = {'fullname':fullname,"url":FRONT_URL+f"verify-user/{instance.uuid}","swedish_default":instance.is_swedishdefault}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
        email_msg = EmailMessage(subject,email_html_template,email_from,recipient_list)
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


@receiver(post_save, sender=BatchSession)
def send_session_email(sender, instance, created, **kwargs):
    print("OUTER")
    for student in instance.batch.students.all():
        html_path = SESSION_INVITATION
        fullname = f'{student.first_name} {student.last_name}'
        if student.usersignup.is_swedishdefault:
            subject = 'Inbjudan till utbildnings tillfälle(n)'
        else:
            subject = 'Invitation to join a course session'
        context_data = {'fullname':fullname, "email":student.email_id,"session_name":instance.session_name,"swedish_default":student.usersignup.is_swedishdefault}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (student.email_id,)
        email_msg = EmailMessage(subject,email_html_template,email_from,recipient_list)
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

