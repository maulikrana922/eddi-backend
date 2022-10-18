import logging
from eddi_app import models
from eddi_app.constants.constants import *
from eddi_app.constants.table_name import *
from datetime import datetime
import datetime
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template
import os
from .notification import send_notification
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from django.core import mail
from django.core.mail import EmailMultiAlternatives
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
# from .models import *

logger = logging.getLogger(__name__)

# def my_cron_job():
#     user = getattr(models,USER_PROFILE_TABLE).objects.get(**{"email_id":"nishant.kabariya@gmail.com"})
#     user.location = "nishantttttttttttttttttt"
#     user.save()
#     logger.warning("Running...logger")
#     print("Running...")

def my_cron_job_course():
    course_data = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{STATUS_ID:1})
    for i in course_data:
        end_date = i.course_starting_date + datetime.timedelta(days=i.course_length)
        if datetime.date.today() >= end_date:
            i.status_id = 2
            i.save()
            users = getattr(models,USER_PAYMENT_DETAIL).objects.filter(**{"course__course_name":i.course_name})
            try:
                connection = mail.get_connection()
                path = 'eddi_app'
                img_dir = 'static'
                image = 'Logo.png'
                file_path = os.path.join(path,img_dir,image)
                with open(file_path,'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', '<{name}>'.format(name=image))
                    img.add_header('Content-Disposition', 'inline', filename=image)
                html_path = 'course_expiry_to_user.html'
                connection.open()
                email_from = settings.EMAIL_HOST_USER
                for j in users:
                    try:
                        user_detail = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID : j.email_id})
                        fullname = f"{user_detail.first_name} {user_detail.last_name}"
                    except Exception as ex:
                        fullname = None
                    context_data = {'course_name':i.course_name, "fullname":fullname}
                    html_content = render_to_string(html_path, context_data)               
                    text_content = "..."                      
                    receiver = j.email_id,
                    msg = EmailMultiAlternatives("Course Expiring!!", text_content, email_from, receiver, connection=connection)                                      
                    msg.attach_alternative(html_content, "text/html")
                    msg.attach(img)
                    msg.send()
                connection.close()
            except Exception as ex:
                pass

            try:
                message = f"{i.course_name}, has Expired"
                # data = getattr(models,USERSIGNUP_TABLE).objects.filter(user_type__user_type = "Admin")
                receiver = [i.email_id for i in users]
                try:
                    # translator= Translator(from_lang='english',to_lang="swedish")
                    message_sv = f"{i.course_name}, has Expired"
                except:
                    pass
                # send_notification(sender, receiver, message, sender_type=None, receiver_type=None)
                send_notification(i.supplier.email_id, receiver, message)
                record_map1 = {}
                record_map1 = {
                    "sender" : i.supplier.email_id,
                    "message" : message,
                    "message_sv" : message_sv,
                }
                for i in receiver:
                    try:
                        record_map1["receiver"] = i
                        getattr(models,"Notification").objects.update_or_create(**record_map1)
                    except Exception as ex:
                        print(ex,"exexe")
                        pass
            except Exception as ex:
                pass




    # user.location = "ok"
    # user.save()
    # logger.info("Running...logger")
    # print("Running...")

def my_cron_job_event():
    event_data = getattr(models,EVENT_AD_TABLE).objects.filter(**{STATUS_ID:1})
    for i in event_data:
        # print(i.event_name, "namememe")
        # print(type(i.start_date), "event")
        # print(i.start_time, "time")
        # print(type(i.start_time), "time")
        # print(datetime.now().strftime("%H:%M:%S"), "time")
        # print(type(datetime.now().strftime("%H:%M:%S")), "time")

        # print(time.strftime("%H:%M:%S", time.localtime()))
        # datetime_str = datetime.strptime(time.strftime("%H:%M:%S", time.localtime()), "%H:%M:%S").time()
        # print(type(datetime_str.time()), "strrr")
        # print(type(time.strftime("%H:%M:%S", time.localtime())))
        # print(type(datetime.strptime(str(datetime.now().strftime("%H:%M:%S")), '%H:%M:%S')))
        # print(datetime.strptime(str(datetime.now().strftime("%H:%M:%S")), '%H:%M:%S'), "okokok")
        # print(date.today(), "okokok")
        # print(type(datetime.today()), "okokok")
        # print(type(date.today()), "dateeee")
        # if i.start_date < date.today() and i.start_time > datetime_str:
        # if i.start_date < date.today():
        #     i.status_id = 1
        #     i.save()
        if datetime.date.today() > i.start_date:
        # if i.start_time > datetime_str.time():
            # i.status_id = 1
            # i.save()
            pass


# def my_cron_job_login():
#     user_data = getattr(models,USERSIGNUP_TABLE).objects.filter(**{STATUS_ID:1, IS_APPROVED_ID:1})
#     for i in user_data:
#         time_diff = datetime.datetime.now() - datetime.datetime.strptime(str(user_data.modified_date_time).split("+")[0], '%Y-%m-%d %H:%M:%S.%f')
#         if time_diff.seconds > 172800:
#             try:
#                 html_path = 'user_reminder.html'
#                 fullname = f'{i.first_name} {i.last_name}'
#                 context_data = {'fullname':fullname}
#                 email_html_template = get_template(html_path).render(context_data)
#                 email_from = settings.EMAIL_HOST_USER
#                 recipient_list = (i.email_id,)
#                 email_msg = EmailMessage('You have been missed!',email_html_template,email_from,recipient_list)
#                 email_msg.content_subtype = 'html'
#                 path = 'eddi_app'
#                 img_dir = 'static'
#                 image = 'Logo.png'
#                 file_path = os.path.join(path,img_dir,image)
#                 with open(file_path,'rb') as f:
#                     img = MIMEImage(f.read())
#                     img.add_header('Content-ID', '<{name}>'.format(name=image))
#                     img.add_header('Content-Disposition', 'inline', filename=image)
#                 email_msg.attach(img)
#                 email_msg.send(fail_silently=False)
#             except:
#                 pass

def my_cron_job_balance():
    supplier_data = getattr(models,"SupplierAccountDetail").objects.all()
    for supplier in supplier_data:
        if supplier.account_id:
            account_balance = stripe.Balance.retrieve(
                    stripe_account=supplier.account_id
            )
            for available_balance in account_balance.available:
                supplier.total_amount_due = "{:.2f}".format(float(available_balance["amount"]/100))
                supplier.save()