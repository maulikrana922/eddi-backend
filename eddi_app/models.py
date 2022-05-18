from django.db import models
import uuid
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sessions.backends.db import SessionStore
from django.db.models.signals import post_save
from django.dispatch import receiver
from email.mime.image import MIMEImage
import os
from django.contrib.sessions.models import Session
import string
from eddi_app.constants.constants import *
from eddi_app.constants.table_name import *
import random
from django.template.loader import get_template
from ckeditor.fields import RichTextField
from eddi_app.constants.constants import *
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.core import mail
from django.template.loader import render_to_string
from django.core.mail import get_connection, EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _



otp = ''


# Create your models here.
def PasswordView():
    global otp
    context = None
    digits = f"{str(string.ascii_letters)}{str(string.digits)}!@#$%^&*()"
    otp = "".join(random.choices(digits, k=6))
    print(otp)
    return otp


class utl_status(models.Model):
    value = models.CharField(max_length=60,blank=True, verbose_name=_("Value"))

    created_by = models.CharField(max_length=100,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100,blank=True)
    modified_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Status Table")

    def __str__(self):
        return str(self.value)

class UserType(models.Model):
    user_type = models.CharField(max_length=60,blank=True, verbose_name=_("User Type"))

    created_by = models.CharField(max_length=100,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100,blank=True)
    modified_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("User Type Table")

    def __str__(self):
        return str(self.user_type)


class approval_status(models.Model):
    # status = models.ManyToManyField(utl_status,null=True,blank=True, verbose_name='Status')
    value = models.CharField(max_length=60,blank=True, verbose_name=_("Value"))
    created_by = models.CharField(max_length=100,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100,blank=True)
    modified_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Approval Status Table")

    def __str__(self):
        return str(self.value)

class UserSignup(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True, verbose_name=_("UUID"))
    first_name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('Last Name'))
    password = models.CharField(max_length=150,blank=True,null=True,verbose_name=_('password'))
    email_id = models.EmailField(unique=True,verbose_name=_('Email ID'))
    password = models.CharField(max_length=150,blank=True,null=True,verbose_name=_('Password'))

    user_type = models.ForeignKey(UserType,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_("User Type"))
    is_first_time_login = models.BooleanField(default=True,verbose_name = _('is First Time Login'))

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))
    is_authenticated = models.BooleanField(default=False, verbose_name=_('is_authenticated'))
    is_login_from = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Is Login From'))
    is_active = models.BooleanField(default=False, verbose_name=_('is_active'))
    is_deleted = models.BooleanField(default=False, verbose_name=_('is_deleted'))
    is_resetpassword = models.BooleanField(default=True, verbose_name=_('is_resetpassword'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True,default=1)

    class Meta:
        verbose_name = _("User Signup Table")


@receiver(post_save, sender=UserSignup)
def send_appointment_confirmation_email(sender, instance, created, **kwargs):
    print("OUTER")
    if created and instance.user_type.user_type == ADMIN_S:
        print("INNER")
        html_path = OTP_EMAIL_HTML
        otp = PasswordView()
        fullname = f'{instance.first_name} {instance.last_name}'
        context_data = {'final_otp':otp,'fullname':fullname}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
        data = UserSignup.objects.get(email_id = instance.email_id)
        data.password = make_password(otp)
        data.save()
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

    if created and instance.user_type.user_type == SUPPLIER_S:
        record_map = {}
        try:
            record_map = {
                "supplier_name" : f"{instance.first_name}{instance.last_name}"
            }
            getattr(models,"SupplierProfile").objects.update_or_create(**record_map)
        except Exception as ex:
            print(ex, "exexexexe")

        print("INNER")
        html_path = OTP_EMAIL_HTML
        otp = PasswordView()
        fullname = f'{instance.first_name} {instance.last_name}'
        context_data = {'final_otp':otp,'fullname':fullname}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
        data = UserSignup.objects.get(email_id = instance.email_id)
        data.password = make_password(otp)
        data.save()
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
    
    if created and instance.user_type.user_type == 'User':
        print("User")
        # welcome user mail
        html_path = USER_WELCOME_HTML
        fullname = f'{instance.first_name} {instance.last_name}'
        context_data = {'fullname':fullname, "uuid": instance.uuid}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
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

    
class NonBuiltInUserToken(Token):
    """
    Overrides the Token model to use the
    non-built-in user model
    """
    user = models.ForeignKey(
        UserSignup, related_name='auth_token',
        on_delete=models.CASCADE, 
        verbose_name=_("email_id")
    )

    class Meta:
        verbose_name = _('Non BuiltIn User Token')




class CourseCategoryDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    category_name = models.CharField(max_length=150,verbose_name=_('Category Name'),blank=True,null=True)
    category_image = models.FileField(upload_to='category_image/',verbose_name=_('Category Image'),blank=True,null=True)

    category_overview = models.CharField(max_length=150,verbose_name=_('Category Overview'),blank=True,null=True)
    key_highlights = models.CharField(max_length=150,verbose_name=_('Key_highlights'),blank=True,null=True)
    key_highlights_description =  RichTextField(verbose_name = _('Key_highlights_Description'),blank = True)
    color = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Color'))
    enrollment_process = models.CharField(max_length=150,verbose_name=_('Enrollment_Process'),blank=True,null=True)
    enrollment_process_description = models.CharField(max_length=2000,verbose_name=_('Enrollment_Process_Description'),blank=True,null=True)
    step_1_text = models.CharField(max_length=150,verbose_name=_('Step_1_text'),blank=True,null=True)
    step_1_description = models.CharField(max_length=2000,verbose_name=_('Step_1_Description'),blank=True,null=True)
    step_2_text = models.CharField(max_length=150,verbose_name=_('Step_2_text'),blank=True,null=True)
    step_2_description = models.CharField(max_length=2000,verbose_name=_('Step_2_Description'),blank=True,null=True)
    step_3_text = models.CharField(max_length=150,verbose_name=_('Step_3_text'),blank=True,null=True)
    step_3_description = models.CharField(max_length=2000,verbose_name=_('Step_3_Description'),blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))
    is_deleted = models.BooleanField(default=False, verbose_name=_('is_deleted'))


    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    # def  image_tag(self):
    #     return mark_safe('<img src="/../../media/%s" width="150" height="150" />' % (self.category_image))

    # image_tag.allow_tags = True

    class Meta:
        verbose_name = _("Course Category Table")

    def __str__(self):
        return self.category_name
    


class CourseSubCategoryDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    category_name = models.ForeignKey(CourseCategoryDetails,on_delete=models.CASCADE,verbose_name=_('Sub Category Name'),blank=True,null=True)
    supplier = models.ForeignKey(UserSignup,on_delete=models.CASCADE,null=True,verbose_name=_('supplier'),blank=True,limit_choices_to={'user_type_id': 1})

    subcategory_name = models.CharField(max_length=150,verbose_name=_('Sub Category Name'),blank=True,null=True)

    subcategory_image = models.FileField(upload_to='category_image/',verbose_name=_('Category Image'),blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    is_approved = models.ForeignKey(approval_status,on_delete=models.CASCADE,verbose_name=_('is_approved'),blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name = _("Course Sub Category Table")

    def __str__(self):
        return self.subcategory_name


class CourseType(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    type_name = models.CharField(max_length=150,verbose_name=_('Course Type Name'),blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name = _("Course Type Table")

    def __str__(self):
        return self.type_name
    

class CourseLevel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    level_name = models.CharField(max_length=150,verbose_name=_('Course Level Name'),blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name = _("Course Level Table")

class FeeType(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    fee_type_name = models.CharField(max_length=150,verbose_name=_('Fee Type Name'),blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name = _("Fee Type Table")

    def __str__(self):
        return self.fee_type_name
    

class InvoiceVATCMS(models.Model):
    vat_value = models.IntegerField(blank=True,null=True,verbose_name=_("VAT Value Percentage"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))

    def __str__(self):
        return str(self.vat_value)

    class Meta:
        verbose_name = _("Invoice VAT Table")



class SupplierOrganizationProfile(models.Model):
    # Organization Information
    supplier_email = models.EmailField(blank=True,null=True,verbose_name=_("Supplier Email"))
    organizational_name = models.CharField(max_length=150,blank=True,null=True,verbose_name=_("Organizational Name"))
    organization_email = models.EmailField(blank=True,null=True,verbose_name=_("Oraganization Email"))
    organization_website = models.CharField(max_length=250,blank=True,null=True,verbose_name=_("organization Website"))
    organization_address = models.TextField(max_length=500,blank=True,null=True,verbose_name=_("Organization Address"))
    country = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Country"))
    city = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("City"))
    brif_information = models.TextField(max_length=250,blank=True,null=True,verbose_name=_("Brief Information on Organization"))
    organization_phone_number = models.CharField(max_length=25,blank=True,null=True,verbose_name=_("Organization Phone Number"))
    contact_person = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Contact Person at Eddi"))
    linkedIn_profile = models.CharField(max_length=200,blank=True,null=True,verbose_name=_("LinkedIn Profile"))
    facebook_profile = models.CharField(max_length=200,blank=True,null=True,verbose_name=_("Facebook Profile"))

    # Course Category
    course_category = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Course Category"))
    sub_category = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Sub Category"))

    # Additional Information
    organization_logo = models.ImageField(upload_to = 'organization_logo/',blank=True,null=True,verbose_name=_('Organization Logo'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))



    class Meta:
        verbose_name = _("Supplier Organization Profile Table")

    def __str__(self):
        return self.supplier_email
    


class CourseDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    supplier = models.ForeignKey(UserSignup,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('supplier'))
    supplier_organization = models.ForeignKey(SupplierOrganizationProfile,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('Supplier Organization'))
    course_image = models.FileField(upload_to='course_image/',verbose_name=_('Course Image'),blank=True,null=True)
    course_name = models.CharField(max_length=150,verbose_name=_('Course Name'),blank=True,null=True)
    course_level = models.ForeignKey(CourseLevel,on_delete=models.CASCADE,verbose_name=_('Course Level'),blank=True,null=True)
    course_length = models.IntegerField(default=0,verbose_name=_('Course Length'),blank=True,null=True)
    course_category = models.ForeignKey(CourseCategoryDetails,on_delete=models.CASCADE,verbose_name=_('Course Category'),blank=True,null=True)
    course_subcategory = models.ForeignKey(CourseSubCategoryDetails,on_delete=models.CASCADE,verbose_name=_('Course Category'),blank=True,null=True)
    course_language = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Course Language'))
    course_starting_date = models.DateField(verbose_name=_('Course Start Date'), blank=True,null=True)
    course_for_organization = models.BooleanField(default=False,verbose_name=_('Course For Organization'))
    organization_domain = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Organization Domain'))
    course_type = models.ForeignKey(CourseType,on_delete=models.CASCADE,verbose_name=_('Course Type'),blank=True,null=True)
    fee_type = models.ForeignKey(FeeType,on_delete=models.CASCADE,verbose_name=_('Fee Type'),blank=True,null=True)
    course_price = models.FloatField(default=0,verbose_name=_('Course Price'),blank=True,null=True)
    var_charges = models.ForeignKey(InvoiceVATCMS,on_delete=models.CASCADE,verbose_name=_('Invoice Vat'),blank=True,null=True)
    additional_information = models.TextField(max_length=1500,verbose_name=_('Additional Information'),blank=True,null=True)
    organization_location = models.CharField(max_length=500,verbose_name=_('Organization Location'),blank=True,null=True)
    sub_area = models.CharField(max_length=300,verbose_name=_('Sub Area'),blank=True,null=True)
    course_checkout_link = models.CharField(max_length=255,verbose_name=_('Checkout Link'),blank=True,null=True)
    meeting_link = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("Meeting Link"))
    meeting_passcode = models.CharField(max_length=200,blank=True,null=True,verbose_name=_("Passcode"))
    target_users = models.CharField(max_length=10000,blank=True,null=True,verbose_name=_("Target Users"))
    

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    is_approved = models.ForeignKey(approval_status,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('is_approved'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name = _("Course Details Table")

    def __str__(self):
        return str(self.course_name)
    
@receiver(post_save, sender=CourseDetails)
def add_organization_domain(sender, instance, created, **kwargs):
    if created and instance.course_for_organization == True:
        
        test_str = instance.supplier.email_id
        res = test_str.split('@')[1]
        print(res)
        CourseDetails.objects.filter(uuid = instance.uuid).update(organization_domain = str(res))

@receiver(post_save, sender=CourseDetails)
def bulk_email(sender, instance, created, **kwargs):
    if instance.course_for_organization == True and instance.target_users:
        connection = mail.get_connection()
        instance.target_users.split(",")
        try:
            reciever_list = instance.target_users.split(",")
        except Exception as ex:
            reciever_list = instance.target_users.split()
        try:
            path = 'eddi_app'
            img_dir = 'static'
            image = 'Logo.jpg'
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
                    username = user_detail.first_name
                except Exception as ex:
                    username = ""
                context_data = {'course_name':instance.course_name, "user_name" : username, "supplier_name" : instance.supplier.first_name, "organization_name" : instance.supplier_organization.organizational_name, "uuid":instance.uuid}
                html_content = render_to_string(html_path, context_data)               
                text_content = "..."                      
                receiver = i,
                msg = EmailMultiAlternatives("Hello", text_content, email_from, receiver, connection=connection)                                      
                msg.attach_alternative(html_content, "text/html")
                msg.attach(img)
                msg.send()                
            connection.close()
        except Exception as ex:
            pass

################## CMS    ###################################

class WhatsonEddiCMS(models.Model):
    content = RichTextField(verbose_name = _("Whats'on Eddi"),blank = True)
    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)
    
    class Meta:
        verbose_name = _("Whats'on Eddi CMS")

class HomePageCMSBanner(models.Model):
    image_title = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Image Title'))
    banner = models.ImageField(upload_to = 'homepage_banner/', verbose_name=_("Banner Image"))

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name = _("Home Page CMS Banner Table")


class HomePageCMSPartners(models.Model):
    image_title = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Image Title'))
    partner_logo = models.ImageField(upload_to = 'homepage_partner_logo/', verbose_name=_("Partner Logo"))

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    def __str__(self):
        return str(self.partner_logo.url)

    class Meta:
        verbose_name = _("Home Page CMS Partners Table")


class ContactFormLead(models.Model):
    fullname = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Full Name'))
    email_id = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    phone_number = models.BigIntegerField(blank=True,null=True,verbose_name=_('Phone Number'))
    message = models.TextField(max_length=500,blank=True,null=True,verbose_name=_('Message'))

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    def __str__(self):
        return str(self.email_id)

    class Meta:
        verbose_name = _("Contact Form Lead Table")

@receiver(post_save, sender=ContactFormLead)
def send_contact_usl(sender, instance, created, **kwargs):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = (settings.EMAIL_HOST_USER,)
    message = f'''Full Name: {instance.fullname}
    Email ID: {instance.email_id}
    Phone Number: {instance.phone_number}
    Message: {instance.message}

    '''
    email_msg = EmailMessage('Contact Us Email',message,email_from,recipient_list)
    email_msg.send(fail_silently=False)


class BlogDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    blog_image = models.ImageField(upload_to = 'blog_image/', verbose_name=_("Blog Image"))
    blog_title = models.CharField(max_length=500,null=True,blank=True,verbose_name=_('Blog Title'))
    blog_description = RichTextField(verbose_name = _('Blog Description'),blank = True)
    blog_category = models.ForeignKey(CourseCategoryDetails,on_delete=models.CASCADE,null=True,blank=True,verbose_name=_("Blog Category"))
    written_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Written by'))

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name = _("Blog Table")

class TestinomialsDetails(models.Model):
    user_id = models.ForeignKey(UserSignup,on_delete=models.CASCADE,null=True,blank=True,verbose_name=_('User Details'))
    review = RichTextField(blank=True,verbose_name = _('User Review'))
    # profile_image = models.ImageField(upload_to = 'blog_image/', blank=True,null=True,verbose_name="Profile Image")
    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=('Modified Date Time'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=('Status'),blank=True,null=True)

    class Meta:
        verbose_name = _("Testinomials Details Table")

class Header_FooterCMS(models.Model):
    # Header
    eddi_logo_header = models.ImageField(upload_to = 'eddi_logo/',blank=True,null=True,verbose_name=_("Eddi Logo Header"))
    button_1_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 1 Text'))
    button_2_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 2 Text'))
    button_3_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 3 Text'))
    button_4_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 4 Text'))
    login_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Login Button Text'))

    # Footer
    eddi_logo_footer = models.ImageField(upload_to = 'eddi_logo/',blank=True,null=True,verbose_name=_("Eddi Logo Footer"))
    description = RichTextField(verbose_name = _('Footer Description'),blank=True)
    follow_us_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Follow Us Text'))
    social_media_icon1 = models.ImageField(upload_to='social_media_icon/',blank=True,null=True,verbose_name=_("Social Media Icon 1"))
    social_media_icon2 = models.ImageField(upload_to='social_media_icon/',blank=True,null=True,verbose_name=_("Social Media Icon 2"))
    social_media_icon3 = models.ImageField(upload_to='social_media_icon/',blank=True,null=True,verbose_name=_("Social Media Icon 3"))
    copyright_text = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Copyright Text'))

    quick_link_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Quicklink Text'))
    quick_link_button_text1 = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Quicklink Button Text1'))
    quick_link_button_text2 = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Quicklink Button Text2'))
    quick_link_button_text3 = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Quicklink Button Text3'))
    quick_link_button_text4 = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Quicklink Button Text4'))
    quick_link_button_text5 = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Quicklink Button Text5'))
    quick_link_button_text6 = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Quicklink Button Text6'))
    
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))

    class Meta:
        verbose_name = _("Header_FooterCMS")

class HomePageCMS(models.Model):

    #section 1
    section_1_image = models.ManyToManyField(HomePageCMSBanner,blank=True,null=True,verbose_name=_('Banner Image'))
    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))


    section_1_description = RichTextField(verbose_name = _('Description'),blank=True)


    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_1_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)

    #section 2
    section_2_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_2_description = RichTextField(verbose_name = _('Description'),blank=True)
    section_2_left_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Left Button Text'))
    section_2_left_button_link = models.URLField(verbose_name=_('Left Button URL'),blank=True,null=True)
    section_2_right_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Right Button Text'))
    section_2_right_button_link = models.URLField(verbose_name=_('Right Button URL'),blank=True,null=True)

    #section 3
    section_3_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_3_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_3_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)

    #section 4
    section_4_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_4_logo = models.ManyToManyField(HomePageCMSPartners,verbose_name=_('Partner Logo'),blank=True,null=True)

    #section 5
    section_5_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_5_blog = models.ManyToManyField(BlogDetails,blank=True,null=True,verbose_name=_("Blog"))

    #section 6
    section_6_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_6_description = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Description"))
    section_6_testinomials = models.ManyToManyField(TestinomialsDetails,blank=True,null=True,verbose_name=_('Testinomials'))

    #section 8
    section_8_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_8_image = models.ImageField(upload_to = 'homepage/',blank=True,null=True,verbose_name=_('Image'))
    section_8_description = RichTextField(verbose_name = _('Description'),blank=True)
    section_8_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_8_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)
   
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    class Meta:
        verbose_name = _("Home Page")

def regions_changed(sender, **kwargs):
    if kwargs['instance'].section_5_blog.count() > 4:
        raise ValidationError("You can't assign more than four regions")

m2m_changed.connect(regions_changed, sender=HomePageCMS.section_5_blog.through)


class AboutUsPageCMS(models.Model):

    #section 1
    section_1_image = models.ImageField(upload_to = 'about_us/',blank=True,null=True,verbose_name=_('Banner Image'))
    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_1_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)

    #section 2
    section_2_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_2_description = RichTextField(verbose_name = _('Description'),blank=True)
    section_2_video = models.FileField(verbose_name=_('Video Upload'),upload_to='about_us/',null=True,blank=True)

    #section 3
    section_3_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_3_image = models.ImageField(upload_to = 'about_us/',blank=True,null=True,verbose_name=_('Image'))
    section_3_description = RichTextField(verbose_name = _('Description'),blank=True)
    section_3_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_3_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)

    #section 4
    section_4_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_4_courses = models.ManyToManyField(CourseDetails,verbose_name=_('Newest Courses'),blank=True,null=True)
    section_4_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_4_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)

   
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    class Meta:
        verbose_name = _("About Us Page")


class ContactUsPageCMS(models.Model):
    
    #section 1
    section_1_image = models.ImageField(upload_to = 'about_us/',blank=True,null=True,verbose_name=_('Banner Image'))
    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_1_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)

    #section 2
    section_2_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_2_address = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Address"))
    section_2_contact = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Contact Number"))
    section_2_email = models.EmailField(blank=True,null=True,verbose_name=_("Email ID"))
    section_2_latitude = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Latitude"))
    section_2_longitude = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Longitude"))

    section_2_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    class Meta:
        verbose_name = _("Contact Us Page")


class PrivacyPolicyCMS(models.Model):
    #section 1
    section_1_image = models.ImageField(upload_to = 'privacy_policy/',blank=True,null=True,verbose_name=_('Banner Image'))
    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_1_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)

    #section 2
    section_2_main_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Main Heading"))
    section_2_left_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Left Heading"))
    section_2_description = RichTextField(verbose_name = _('Description'),blank=True)
    section_2_sub_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Sub Heading"))
    section_2_sub_description = RichTextField(verbose_name = _('Sub Description'),blank=True)
    section_2_last_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Last Heading"))
    section_2_last_description = RichTextField(verbose_name = _('Last Description'),blank=True)

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    class Meta:
        verbose_name = _("Privacy Policy Page")


class PrivacyPolicyCMSSupplier(models.Model):
    #section 1
    section_1_image = models.ImageField(upload_to = 'privacy_policy/',blank=True,null=True,verbose_name=_('Banner Image'))
    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_1_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)

    #section 2
    section_2_main_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Main Heading"))
    section_2_left_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Left Heading"))
    section_2_description = RichTextField(verbose_name = _('Description'),blank=True)
    section_2_sub_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Sub Heading"))
    section_2_sub_description = RichTextField(verbose_name = _('Sub Description'),blank=True)
    section_2_last_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Last Heading"))
    section_2_last_description = RichTextField(verbose_name = _('Last Description'),blank=True)

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    class Meta:
        verbose_name = _("Privacy Policy Page Supplier")

class TermsConditionCMS(models.Model):
    #section 1
    section_1_image = models.ImageField(upload_to = 'terms_conditon/',blank=True,null=True,verbose_name=_('Banner Image'))

    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_1_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)
    #section 2
    section_2_main_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Main Heading"))
    section_2_left_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Left Heading"))
    section_2_description = RichTextField(verbose_name = _('Description'),blank=True)

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    class Meta:
        verbose_name = _("Terms & Condition Page")


class TermsConditionCMSSupplier(models.Model):
    #section 1
    section_1_image = models.ImageField(upload_to = 'terms_conditon/',blank=True,null=True,verbose_name=_('Banner Image'))

    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_1_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)
    #section 2
    section_2_main_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Main Heading"))
    section_2_left_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Left Heading"))
    section_2_description = RichTextField(verbose_name = _('Description'),blank=True)

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    class Meta:
        verbose_name = _("Terms & Condition Page Supplier")



class UserProfile(models.Model):

    #personal information
    usersignup = models.ForeignKey(UserSignup,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('User Signup'))
    email_id = models.CharField(max_length=255,blank=True,null=True,verbose_name=_("Email Id"),unique=True)
    profile_image = models.ImageField(upload_to = 'profile_image/',blank=True,null=True,verbose_name=_('Profile Image'))
    first_name = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("First Name"))
    last_name = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Last Name"))
    gender = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Gender"))
    location = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("location"))
    dob = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Date of Birth"))
    personal_number = models.IntegerField(blank=True,null=True,verbose_name=_("Personal Number"))
    phone_number = models.BigIntegerField(blank=True,null=True,verbose_name=_("Phone Number"))

    #Educational Information
    highest_education = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Highest Level of Education"))
    university_name = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("University Name"))
    highest_degree = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Highest Degree"))
    educational_area = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Educational Area"))
    other_education = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Other Relavant Education"))
    diplomas_certificates = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Diplomas and Certificates"))

    #Professional Information
    current_professional_role = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Current Professional Role"))
    additional_role = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Additional Role"))
    extra_curricular = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Extra Curricular You Want"))
    extra_curricular_competence = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Extra Curricular Competence You Have"))
    core_responsibilities = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Core Responsibilities"))
    level_of_role = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Level Of Role"))
    future_professional_role = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Future Professional Role"))

    #area of interest
    course_category = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Course Categories"))
    user_interests = models.JSONField(blank=True,null=True, verbose_name=_("User Interests"))
    area_of_interest = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Area of Interest"))
    agree_ads_terms = models.BooleanField(default=True,verbose_name=_('agree ads terms'))
    is_deleted = models.BooleanField(default=False, verbose_name=_('is_deleted'))

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    class Meta:
        verbose_name = _("User Eddi Profile")


    def __str__(self):
        return str(self.email_id)
    

class CourseRating(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('user'))
    course_name = models.ForeignKey(CourseDetails,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('course_name'))
    star = models.CharField(max_length=150,verbose_name=_('Star'),blank=True,null=True)
    comment = models.TextField(max_length=5000,verbose_name=_('Comment'),blank=True,null=True)
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))

    class Meta:
        verbose_name = _("Course Rating Table")

    # def __str__(self):
    #     return self.course_name
    


class UserPersonalProfile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    profile_image = models.ImageField(upload_to = 'profile_image/',blank=True,null=True,verbose_name=_('Profile Image'))
    full_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Full Name"))
    location = models.CharField(max_length=300, blank=True, null=True, verbose_name=_("Location"))
    phone_number = models.BigIntegerField(blank=True,null=True,verbose_name=_("Phone Number"))
    email_id = models.CharField(max_length=255,blank=True,null=True,verbose_name=_("Email Id"),unique=True)

    class Meta:
        verbose_name = _("User Personal Profile")


class SupplierProfile(models.Model):
    supplier_email = models.EmailField(blank=True,null=True,verbose_name=_("Supplier Email"))
    supplier_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Supplier Name"))
    account_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Account Number"))
    account_holder_name = models.CharField(max_length=200,blank=True,null=True,verbose_name=_("Account Holder Name"))
    ifsc_code = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("IFSC Code"))
    address = models.TextField(max_length=500,blank=True,null=True,verbose_name=_("Address"))
    phone_number = models.BigIntegerField(blank=True,null=True,verbose_name=_("Phone Number"))
    about_me = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("About Me"))
    supplier_image = models.ImageField(upload_to = 'supplier_image/',blank=True,null=True,verbose_name=_('Supplier Image'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    def __str__(self):
        return str(self.supplier_name)

    class Meta:
        verbose_name = _("Supplier Profile")


class UserPaymentDetail(models.Model):
    course_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Course name"))
    email_id = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    card_type = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Card Type"))
    amount = models.FloatField(blank=True,null=True,verbose_name=_("Amount"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Payment Created Date Time'))
    status = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Payment Status"))

    class Meta:
        verbose_name = _("User Payment Detail")

    def __str__(self):
        return self.course_name
    
class FavouriteCourse(models.Model):
    course_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Course Name"))
    email_id = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    is_favourite = models.BooleanField(default=False,verbose_name=_('is_favourite'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Favourite Course Created Date Time'))
    
    def __str__(self):
        return str(self.course_name)

    class Meta:
        verbose_name = _("Favourite Course")
    


class CourseEnroll(models.Model):
    course_category = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Course Category"))
    supplier_email = models.EmailField(blank=True,null=True,verbose_name=_('supplier email'))
    payment_detail = models.ForeignKey(UserPaymentDetail,on_delete=models.CASCADE,verbose_name=_('Payment Detail'),blank=True,null=True)
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE,verbose_name=_('User Profile'),blank=True,null=True)
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Favourite Course Created Date Time'))


    def __str__(self):
        return str(self.payment_detail.course_name)

    class Meta:
        verbose_name = _("Course Enroll")  

    
@receiver(post_save, sender=CourseEnroll)
def send_appointment_confirmation_email(sender, instance, created, **kwargs):
    if created:
        html_path = COURSE_ENROLL_HTML_TO_S
        fullname = f'{instance.user_profile.first_name} {instance.user_profile.last_name}'
        category = f'{instance.course_category}'
        context_data = {'fullname':fullname, "course_category":category}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.supplier_email,)
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




class EventAd(models.Model):    
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    event_image = models.FileField(upload_to='event_image/',verbose_name=_('Event Image'),blank=True,null=True)
    event_choose_type = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Choose Type"))
    event_publish_on = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Publish on"))
    event_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Name"))
    event_category = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Category"))
    banner_video_link =  models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Banner Link"))
    start_date = models.DateField(verbose_name=_('Event Start Date'), blank=True,null=True)
    start_time = models.TimeField(verbose_name=_('Event Start Time'), blank=True,null=True)
    fees_type = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Fees Type"))
    event_type = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Type"))
    event_price = models.FloatField(default=0,verbose_name=_('Event Price'),blank=True,null=True)
    checkout_link =  models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Checkout Link"))
    meeting_link = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("Meeting Link"))
    meeting_passcode = models.CharField(max_length=200,blank=True,null=True,verbose_name=_("Passcode"))
    event_small_description = RichTextField(verbose_name = _('Event Small Description'), blank = True, null=True)
    event_description = RichTextField(verbose_name = _('Event Description'), blank = True, null=True)
    event_location = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("Location"))
    event_organizer = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Organizer"))
    event_subscriber = models.IntegerField(default=0,verbose_name=_('Course Subscriber'),blank=True,null=True)
    is_featured = models.BooleanField(default=False,verbose_name=_('is_featured'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('EventAd Created Date Time'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True, default=1)


    class Meta:
        verbose_name = _("EventAd Table")

    def __str__(self):
        return str(self.event_name)



class EventAdPaymentDetail(models.Model):
    event_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Name"))
    email_id = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    card_type = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Card Type"))
    amount = models.FloatField(blank=True,null=True,verbose_name=_("Amount"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Payment Created Date Time'))
    status = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Payment Status"))


    def __str__(self):
        return str(self.event_name)

    class Meta:
        verbose_name = _("Event Ad Payment Detail") 

class EventAdEnroll(models.Model):
    event_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event name"))
    user_email = models.EmailField(blank=True,null=True,verbose_name=_('User Email'))
    payment_detail = models.ForeignKey(EventAdPaymentDetail,on_delete=models.CASCADE,verbose_name=_('Payment Detail'),blank=True,null=True)
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE,verbose_name=_('User Profile'),blank=True,null=True)
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))

    def __str__(self):
        return str(self.event_name)

    class Meta:
        verbose_name = _("Event Ad Enroll")
    

class MaterialVideoMaterial(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    video_file = models.FileField(upload_to='course_material_video/',verbose_name=_('Video Files'),blank=True,null=True)
    actual_duration = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Actual Video Duration"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))

    # def __str__(self):
    #     return str(self.video_file) + " " + str(self.uuid)
    
    # class Meta:
    #     verbose_name = _("Material Video Material")

class MaterialDocumentMaterial(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    document_file = models.FileField(upload_to='course_material_doc/',verbose_name=_('Document Files'),blank=True,null=True)
    file_size = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("File Size"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))

    def __str__(self):
        return str(self.document_file)

    class Meta:
        verbose_name = _("Material Document Material")


class CourseMaterialStatus(models.Model):
    user_email = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Email'))
    video_id = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Video'))
    document_id = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Document'))
    is_complete = models.BooleanField(default=False,verbose_name=_('is_complete'))
    duration = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Duration'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))

    def __str__(self):
        return str(self.video_id)

    class Meta:
        verbose_name = _("Course Material Status")
    


class CourseMaterial(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True, verbose_name=_('UUID'))
    course = models.ForeignKey(CourseDetails,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_("Course"))
    video_title = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Video Title"))
    video_files = models.ManyToManyField(MaterialVideoMaterial,verbose_name=_('Video Files'),blank=True,null=True)
    file_title = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("File Title"))
    document_files = models.ManyToManyField(MaterialDocumentMaterial,verbose_name=_('Document Files'),blank=True,null=True)
    # material_status = models.ManyToManyField(CourseMaterialStatus,verbose_name='CourseMaterialStatus',blank=True,null=True)
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))

    def __str__(self):
        return self.course.course_name
    
    # class Meta:
    #     verbose_name = _("Course Material")


# class CourseCompleteStatus(models.Model):
#     course_material = models.ForeignKey(CourseMaterial,on_delete=models.CASCADE,blank=True,null=True,verbose_name="Course Material")
#     user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,blank=True,null=True,verbose_name="User")


class RecruitmentAd(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    recruitmentAd_File = models.FileField(upload_to='recruitment_file/',verbose_name=_('Recruitment File'),blank=True,null=True)
    recruitmentAd_title = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("RecruitmentAd Title"))
    recruitmentAd_description = RichTextField(verbose_name = _('RecruitmentAd Description'), blank = True, null=True)
    recruitmentAd_banner_video_link =  models.CharField(max_length=500,blank=True,null=True,verbose_name=_("RecruitmentAd Banner Link"))
    supplier_profile = models.ForeignKey(SupplierProfile,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('Supplier Profile'))
    user_profile = models.ManyToManyField(UserProfile,verbose_name=_('User Profile'),blank=True,null=True)
    recruitmentAd_Expiry =  models.DateField(verbose_name=_('RecruitmentAd Expiry Date'), blank=True,null=True)
    subscriber_count = models.IntegerField(default=0,verbose_name=_('Subscriber Count'),blank=True,null=True)
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))
    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    is_approved = models.ForeignKey(approval_status, on_delete=models.CASCADE, verbose_name=_('Approval Status'), blank=True,null=True, default=None)
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True, default=None)

    class Meta:
        verbose_name = _("Recruitment Ad")
        

class InvoiceData(models.Model):
    invoice_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Invoice Number'))
    user_address = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('User Address'))
    vat_charges = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Vat'))
    user_email = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    course_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Course Name'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))

    def __str__(self):
        return str(self.course_name)
    
    class Meta:
        verbose_name = _("Invoice Data")


class InvoiceDataEvent(models.Model):
    invoice_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Invoice Number'))
    user_address = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('User Address'))
    vat_charges = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Vat'))
    user_email = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    event_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Event Name'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))

    def __str__(self):
        return str(self.event_name)
    
    class Meta:
        verbose_name = _("Invoice Data Event")


class Notification(models.Model):
    sender = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('sender'))
    receiver = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('receiver'))
    user_type = models.ForeignKey(USERSIGNUP_TABLE,on_delete=models.CASCADE,verbose_name=_('User Type'),blank=True,null=True,default=None)
    user_detail = models.ForeignKey(USER_PROFILE_TABLE,on_delete=models.CASCADE,verbose_name=_('User Email'),blank=True,null=True,default=None)
    supplier_detail = models.ForeignKey(SUPPLIER_PROFILE_TABLE,on_delete=models.CASCADE,verbose_name=_('Supplier Email'),blank=True,null=True,default=None)
    message = models.TextField(max_length=2000,blank=True,null=True,verbose_name=_("Address"))
    is_clear = models.BooleanField(default=False,verbose_name=_('is_clear'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))

    class Meta:
        verbose_name = _("Notification Table")

