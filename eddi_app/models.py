from django.db import models
import uuid
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from email.mime.image import MIMEImage
import os
import string
from eddi_app.constants.constants import *
from eddi_app.constants.table_name import *
import random
from django.template.loader import get_template
from ckeditor.fields import RichTextField
from eddi_app.constants.constants import *
from django.contrib.auth.hashers import make_password
from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.core import mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _
from .notification import send_notification, send_push_notification
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


class utl_status(models.Model):
    value = models.CharField(max_length=60,blank=True, verbose_name=_("Value"))

    created_by = models.CharField(max_length=100,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100,blank=True)
    modified_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _("Status Table")


    def __str__(self):
        return str(self.value)

class UserType(models.Model):
    user_type = models.CharField(max_length=60,blank=True, verbose_name=_("User Type"))

    created_by = models.CharField(max_length=100,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100,blank=True)
    modified_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _("User Type Table")

    def __str__(self):
        return str(self.user_type)


class approval_status(models.Model):
    value = models.CharField(max_length=60,blank=True, verbose_name=_("Value"))
    created_by = models.CharField(max_length=100,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100,blank=True)
    modified_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _("Approval Status Table")

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
    is_first_time_login = models.BooleanField(default=True,verbose_name = _('Is First Time Login'))

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))
    is_authenticated = models.BooleanField(default=False, verbose_name=_('Is_authenticated'))
    is_login_from = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Is Login From'))
    is_active = models.BooleanField(default=False, verbose_name=_('Is_active'))
    is_deleted = models.BooleanField(default=False, verbose_name=_('Is_deleted'))
    is_resetpassword = models.BooleanField(default=True, verbose_name=_('Is_resetpassword'))
    is_approved = models.ForeignKey(approval_status,on_delete=models.CASCADE,verbose_name=_('is_approved'),blank=True,null=True)
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True,default=1)

    class Meta:
        verbose_name_plural = _("User Signup Table")
    
    def __str__(self):
        return self.email_id
    



    
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
        verbose_name_plural = _('Non BuiltIn User Token')




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

    class Meta:
        verbose_name_plural = _("Course Category Table")

    def __str__(self):
        return self.category_name
    


class CourseSubCategoryDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    category_name = models.ForeignKey(CourseCategoryDetails,on_delete=models.CASCADE,verbose_name=_('Sub Category Name'),blank=True,null=True)
    supplier = models.ForeignKey(UserSignup,on_delete=models.CASCADE,null=True,verbose_name=_('Supplier'),blank=True,limit_choices_to={'user_type_id': 1})
    subcategory_name = models.CharField(max_length=150,verbose_name=_('Sub Category Name'),blank=True,null=True)
    subcategory_image = models.FileField(upload_to='category_image/',verbose_name=_('Category Image'),blank=True,null=True)
    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))
    is_approved = models.ForeignKey(approval_status,on_delete=models.CASCADE,verbose_name=_('Is_approved'),blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name_plural = _("Course Sub Category Table")

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
        verbose_name_plural = _("Course Type Table")

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
        verbose_name_plural = _("Course Level Table")

class FeeType(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    fee_type_name = models.CharField(max_length=150,verbose_name=_('Fee Type Name'),blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name_plural = _("Fee Type Table")

    def __str__(self):
        return self.fee_type_name
    

class InvoiceVATCMS(models.Model):
    vat_value = models.IntegerField(blank=True,null=True,verbose_name=_("VAT Value Percentage"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))

    def __str__(self):
        return str(self.vat_value)

    class Meta:
        verbose_name_plural = _("Invoice VAT Table")

class PlatformFeeCMS(models.Model):
    platform_fee = models.IntegerField(blank=True,null=True,verbose_name=_("Platform Fee Value Percentage"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))

    def __str__(self):
        return str(self.platform_fee)

    class Meta:
        verbose_name_plural = _("Platform Fee Table")

class SupplierOrganizationProfile(models.Model):
    # Organization Information
    usersignup = models.ForeignKey(UserSignup,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('User Signup'))
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
    reject_reason = models.CharField(max_length=2000,blank=True,null=True,verbose_name=_("Reject_Rason"))
    approved_once = models.BooleanField(default=False,verbose_name=_('Approved Once'))

    # Course Category
    course_category = models.CharField(max_length=1000,blank=True,null=True,verbose_name=_("Course Category"))
    sub_category = models.CharField(max_length=1000,blank=True,null=True,verbose_name=_("Sub Category"))
    rejection_count = models.IntegerField(default=0,verbose_name=_('Rejection Count'),blank=True,null=True)

    # Additional Information
    organization_logo = models.ImageField(upload_to = 'organization_logo/',blank=True,null=True,verbose_name=_('Organization Logo'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))
    is_approved = models.ForeignKey(approval_status,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('is_approved'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name_plural = _("Supplier Organization Profile Table")

    def __str__(self):
        return self.supplier_email
    


class CourseDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    supplier = models.ForeignKey(UserSignup,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('supplier'),related_name='supplier')
    supplier_organization = models.ForeignKey(SupplierOrganizationProfile,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('Supplier Organization'))
    course_image = models.FileField(upload_to='course_image/',verbose_name=_('Course Image'),blank=True,null=True)
    course_name = models.CharField(max_length=150,verbose_name=_('Course Name'),blank=True,null=True)
    course_level = models.ForeignKey(CourseLevel,on_delete=models.CASCADE,verbose_name=_('Course Level'),blank=True,null=True)
    course_length = models.IntegerField(default=0,verbose_name=_('Course Length'),blank=True,null=True)
    course_category = models.ForeignKey(CourseCategoryDetails,on_delete=models.CASCADE,verbose_name=_('Course Category'),blank=True,null=True)
    course_subcategory = models.ForeignKey(CourseSubCategoryDetails,on_delete=models.CASCADE,verbose_name=_('Course SubCategory'),blank=True,null=True)
    course_language = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Course Language'))
    course_starting_date = models.DateField(verbose_name=_('Course Start Date'), blank=True,null=True)
    course_for_organization = models.BooleanField(default=False,verbose_name=_('Course For Organization'))
    organization_domain = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Organization Domain'))
    course_type = models.ForeignKey(CourseType,on_delete=models.CASCADE,verbose_name=_('Course Type'),blank=True,null=True)
    fee_type = models.ForeignKey(FeeType,on_delete=models.CASCADE,verbose_name=_('Fee Type'),blank=True,null=True)
    course_price = models.CharField(max_length=100,verbose_name=_('Course Price'),blank=True,null=True)
    offer_price = models.CharField(max_length=100,verbose_name=_('Offer Price'),blank=True,null=True)
    var_charges = models.ForeignKey(InvoiceVATCMS,on_delete=models.CASCADE,verbose_name=_('Invoice Vat'),blank=True,null=True)
    additional_information = models.TextField(max_length=1500,verbose_name=_('Additional Information'),blank=True,null=True)
    organization_location = models.CharField(max_length=500,verbose_name=_('Organization Location'),blank=True,null=True)
    sub_area = models.CharField(max_length=300,verbose_name=_('Sub Area'),blank=True,null=True)
    course_checkout_link = models.CharField(max_length=255,verbose_name=_('Checkout Link'),blank=True,null=True)
    meeting_link = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("Meeting Link"))
    meeting_passcode = models.CharField(max_length=200,blank=True,null=True,verbose_name=_("Passcode"))
    is_post = models.BooleanField(default=False,verbose_name=_('Is_post'))
    target_users = models.CharField(max_length=10000,blank=True,null=True,verbose_name=_("Target Users"))
    course_expiry = models.DateField(verbose_name =_('Course Expiry Date'), blank=True,null=True)
    author_name = models.CharField(max_length=150,verbose_name=_('Author Name'),blank=True,null=True)
    author_bio = models.TextField(blank=True,null=True,verbose_name=_('Author bio'))
    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    is_approved = models.ForeignKey(approval_status,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('is_approved'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name_plural = _("Course Details Table")

    def __str__(self):
        return str(self.course_name)
    
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
                    username = user_detail.first_name
                except Exception as ex:
                    username = None
                try:
                    organization_data = instance.supplier_organization.organizational_name
                except Exception as ex:
                    print(ex,"exxx")
                    organization_data = None
                context_data = {'course_name':instance.course_name, "user_name" : username, "supplier_name" : instance.supplier.first_name, "organization_name" : organization_data, "url":FRONT_URL+f"view-course-details/{instance.uuid}/"  }
                html_content = render_to_string(html_path, context_data)               
                text_content = "..."                      
                receiver = i,
                msg = EmailMultiAlternatives("Congratulations!!", text_content, email_from, receiver, connection=connection)                                      
                msg.attach_alternative(html_content, "text/html")
                msg.attach(img)
                msg.send()
            connection.close()
            instance.is_post = False
            instance.save()
        except Exception as ex:
            print(ex,"exx")
            pass


#############################  CMS  ###################################

class WhatsonEddiCMS(models.Model):
    content = RichTextField(verbose_name = _("Whats'on Eddi"),blank = True)
    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)
    
    class Meta:
        verbose_name_plural = _("Whats'on Eddi CMS")

class WhatsonEddiCMS_SV(models.Model):
    content = RichTextField(verbose_name = _("Whats'on Eddi"),blank = True)
    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)
    
    class Meta:
        verbose_name_plural = _("Whats'on Eddi CMS SV")

class HomePageCMSBanner(models.Model):
    image_title = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Image Title'))
    banner = models.ImageField(upload_to = 'homepage_banner/', verbose_name=_("Banner Image"))
    description = RichTextField(verbose_name = _('Description'),blank=True)
    button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name_plural = _("Home Page CMS Banner Table")


class HomePageCMSBanner_SV(models.Model):
    image_title = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Image Title'))
    banner = models.ImageField(upload_to = 'homepage_banner/', verbose_name=_("Banner Image"))
    description = RichTextField(verbose_name = _('Description'),blank=True)
    button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    class Meta:
        verbose_name_plural = _("Home Page CMS Banner Table SV")


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
        verbose_name_plural = _("Home Page CMS Partners Table")


class HomePageCMSPartners_SV(models.Model):
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
        verbose_name_plural = _("Home Page CMS Partners Table SV")


class ContactFormLead(models.Model):
    fullname = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Full Name'))
    email_id = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    phone_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Phone Number'))
    message = models.TextField(max_length=500,blank=True,null=True,verbose_name=_('Message'))

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    def __str__(self):
        return str(self.email_id)

    class Meta:
        verbose_name_plural = _("Contact Form Lead Table")


class ContactFormLead_SV(models.Model):
    fullname = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Full Name'))
    email_id = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    phone_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Phone Number'))
    message = models.TextField(max_length=500,blank=True,null=True,verbose_name=_('Message'))

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True)

    def __str__(self):
        return str(self.email_id)

    class Meta:
        verbose_name_plural = _("Contact Form Lead Table SV")

@receiver(post_save, sender=ContactFormLead)
@receiver(post_save, sender=ContactFormLead_SV)
def send_contactlead_email(sender, instance, created, **kwargs):
    if created:
        html_path = CONTACT_LEAD
        context_data = {'fullname':instance.fullname, "email":instance.email_id, "phone":instance.phone_number, "msg":instance.message}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ('jap.d@latitudetechnolabs.com',)
        email_msg = EmailMessage('General Inquiry from User',email_html_template,email_from,recipient_list)
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
        context_data = {'fullname':instance.fullname}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
        email_msg = EmailMessage('Inquiry Submitted',email_html_template,email_from,recipient_list)
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
        verbose_name_plural = _("Blog Table")


class BlogDetails_SV(models.Model):
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
        verbose_name_plural = _("Blog Table SV")

class TestinomialsDetails(models.Model):
    user_id = models.ForeignKey(UserSignup,on_delete=models.CASCADE,null=True,blank=True,verbose_name=_('User Details'))
    review = RichTextField(blank=True,verbose_name = _('User Review'))
    profile_image = models.ImageField(upload_to = 'blog_image/', blank=True,null=True,verbose_name="Profile Image")
    user_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=('UserName'))
    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=('Modified Date Time'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=('Status'),blank=True,null=True)

    class Meta:
        verbose_name_plural = _("Testinomials Details Table")

class TestinomialsDetails_SV(models.Model):
    user_id = models.ForeignKey(UserSignup,on_delete=models.CASCADE,null=True,blank=True,verbose_name=_('User Details'))
    review = RichTextField(blank=True,verbose_name = _('User Review'))
    profile_image = models.ImageField(upload_to = 'blog_image/', blank=True,null=True,verbose_name="Profile Image")
    user_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=('UserName'))
    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=('Created By'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=('Created Date Time'))
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name=('Modified By'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=('Modified Date Time'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=('Status'),blank=True,null=True)

    class Meta:
        verbose_name_plural = _("Testinomials Details Table SV")

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
        verbose_name_plural = _("Header_FooterCMS")

class Header_FooterCMS_SV(models.Model):
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
        verbose_name_plural = _("Header_FooterCMS SV")


class HomePageCMS(models.Model):

    #section 1
    section_1_image = models.ManyToManyField(HomePageCMSBanner,blank=True,null=True,verbose_name=_('Banner'))


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
        verbose_name_plural = _("Home Page")

def regions_changed(sender, **kwargs):
    if kwargs['instance'].section_5_blog.count() > 4:
        raise ValidationError("You can't assign more than four regions")

m2m_changed.connect(regions_changed, sender=HomePageCMS.section_5_blog.through)


class HomePageCMS_SV(models.Model):

    #section 1
    section_1_image = models.ManyToManyField(HomePageCMSBanner_SV,blank=True,null=True,verbose_name=_('Banner'))

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
    section_4_logo = models.ManyToManyField(HomePageCMSPartners_SV,verbose_name=_('Partner Logo'),blank=True,null=True)

    #section 5
    section_5_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_5_blog = models.ManyToManyField(BlogDetails_SV,blank=True,null=True,verbose_name=_("Blog"))

    #section 6
    section_6_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_6_description = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Description"))
    section_6_testinomials = models.ManyToManyField(TestinomialsDetails_SV,blank=True,null=True,verbose_name=_('Testinomials'))

    #section 8
    section_8_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name=_("Heading"))
    section_8_image = models.ImageField(upload_to = 'homepage/',blank=True,null=True,verbose_name=_('Image'))
    section_8_description = RichTextField(verbose_name = _('Description'),blank=True)
    section_8_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button Text'))
    section_8_button_link = models.URLField(verbose_name=_('Button URL'),blank=True,null=True)
   
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    class Meta:
        verbose_name_plural = _("Home Page SV")

# def regions_changed(sender, **kwargs):
#     if kwargs['instance'].section_5_blog.count() > 4:
#         raise ValidationError("You can't assign more than four regions")

# m2m_changed.connect(regions_changed, sender=HomePageCMS_SV.section_5_blog.through)


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
        verbose_name_plural = _("About Us Page")


class AboutUsPageCMS_SV(models.Model):

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
        verbose_name_plural = _("About Us Page SV")


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
        verbose_name_plural = _("Contact Us Page")


class ContactUsPageCMS_SV(models.Model):
    
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
        verbose_name_plural = _("Contact Us Page SV")


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
        verbose_name_plural = _("Privacy Policy Page")


class PrivacyPolicyCMS_SV(models.Model):
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
        verbose_name_plural = _("Privacy Policy Page SV")


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
        verbose_name_plural = _("Privacy Policy Page Supplier")


class PrivacyPolicyCMSSupplier_SV(models.Model):
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
        verbose_name_plural = _("Privacy Policy Page Supplier SV")

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
        verbose_name_plural = _("Terms & Condition Page")

class TermsConditionCMS_SV(models.Model):
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
        verbose_name_plural = _("Terms & Condition Page SV")


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
        verbose_name_plural = _("Terms & Condition Page Supplier")

class TermsConditionCMSSupplier_SV(models.Model):
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
        verbose_name_plural = _("Terms & Condition Page Supplier SV")


# class AdminProfile(models.Model):
#     admin_email = models.EmailField(blank=True,null=True,verbose_name=_("Admin Email"))
#     admin_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Admin Name"))
#     address = models.TextField(max_length=1000,blank=True,null=True,verbose_name=_("Address"))
#     phone_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Phone Number"))
#     about_me = models.CharField(max_length=1000,blank=True,null=True,verbose_name=_("About Me"))
#     admin_image = models.ImageField(upload_to = 'admin_image/',blank=True,null=True,verbose_name=_('Admin Image'))
#     created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
#     modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

#     def __str__(self):
#         return str(self.admin_name)

#     class Meta:
#         verbose_name_plural = _("Admin Profile")


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
    personal_number = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Personal Number"))
    phone_number = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("Phone Number"))

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
    course_category = models.CharField(max_length=1000,blank=True,null=True,verbose_name=_("Course Categories"))
    user_interests = models.JSONField(blank=True,null=True, verbose_name=_("User Interests"))
    area_of_interest = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Area of Interest"))
    agree_ads_terms = models.BooleanField(default=True,verbose_name=_('agree ads terms'))
    is_deleted = models.BooleanField(default=False, verbose_name=_('is_deleted'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    class Meta:
        verbose_name_plural = _("User Eddi Profile")

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
        verbose_name_plural = _("Course Rating Table") 


class UserPersonalProfile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    profile_image = models.ImageField(upload_to = 'profile_image/',blank=True,null=True,verbose_name=_('Profile Image'))
    full_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Full Name"))
    location = models.CharField(max_length=300, blank=True, null=True, verbose_name=_("Location"))
    phone_number = models.CharField(max_length=50, blank=True, null=True,verbose_name=_("Phone Number"))
    email_id = models.CharField(max_length=255,blank=True,null=True,verbose_name=_("Email Id"),unique=True)

    class Meta:
        verbose_name_plural = _("User Personal Profile")


class SupplierProfile(models.Model):
    supplier_email = models.EmailField(blank=True,null=True,verbose_name=_("Supplier Email"))
    supplier_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Supplier Name"))
    account_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Account Number"))
    account_holder_name = models.CharField(max_length=200,blank=True,null=True,verbose_name=_("Account Holder Name"))
    ifsc_code = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("IFSC Code"))
    address = models.TextField(max_length=500,blank=True,null=True,verbose_name=_("Address"))
    phone_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Phone Number"))
    about_me = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("About Me"))
    supplier_image = models.ImageField(upload_to = 'supplier_image/',blank=True,null=True,verbose_name=_('Supplier Image'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Modified Date Time'))

    def __str__(self):
        return str(self.supplier_name)

    class Meta:
        verbose_name_plural = _("Supplier Profile")



    
class FavouriteCourse(models.Model):
    course_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Course Name"))
    email_id = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    is_favourite = models.BooleanField(default=False,verbose_name=_('is_favourite'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Favourite Course Created Date Time'))
    
    def __str__(self):
        return str(self.course_name)

    class Meta:
        verbose_name_plural = _("Favourite Course")


    



class EventAd(models.Model):    
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    admin_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Admin Name"))
    admin_email = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Admin Email"))
    event_image = models.FileField(upload_to='event_image/',verbose_name=_('Event Image'),blank=True,null=True)
    event_choose_type = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Choose Type"))
    event_publish_on = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Publish on"))
    event_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Name"))
    event_category = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Category"))
    banner_video_link =  models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Banner Link"))
    start_date = models.DateField(verbose_name=_('Event Start Date'), blank=True,null=True)
    end_date = models.DateField(verbose_name=_('Event End Date'), blank=True,null=True)
    start_time = models.TimeField(verbose_name=_('Event Start Time'), blank=True,null=True)
    fees_type = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Fees Type"))
    event_type = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Type"))
    event_price = models.CharField(max_length=100,verbose_name=_('Event Price'),blank=True,null=True)
    original_price = models.CharField(max_length=100,verbose_name=_('Event Original Price'),blank=True,null=True)
    checkout_link =  models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Checkout Link"))
    meeting_link = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("Meeting Link"))
    meeting_passcode = models.CharField(max_length=200,blank=True,null=True,verbose_name=_("Passcode"))
    event_small_description = RichTextField(verbose_name = _('Event Small Description'), blank = True, null=True)
    event_description = RichTextField(verbose_name = _('Event Description'), blank = True, null=True)
    event_location = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("Location"))
    event_organizer = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Organizer"))
    event_subscriber = models.IntegerField(default=0,verbose_name=_('Course Subscriber'),blank=True,null=True)
    event_for_organization = models.BooleanField(default=False,verbose_name=_('Event For Organization'))
    organization_domain = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Organization Domain'))
    is_featured = models.BooleanField(default=False,verbose_name=_('is_featured'))
    is_deleted = models.BooleanField(default=False,verbose_name=_('is_deleted'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('EventAd Created Date Time'))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_('Status'),blank=True,null=True, default=1)



    def __str__(self):
        return str(self.event_name)
        
    class Meta:
        verbose_name_plural = _("EventAd Table")



class MaterialVideoMaterial(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    video_file = models.FileField(upload_to='course_material_video/',max_length=1000, verbose_name=_('Video Files'),blank=True,null=True)
    video_name = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("Video Name"))
    actual_duration = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Actual Video Duration"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))
    
    class Meta:
        verbose_name_plural = _("Material Video Material")

class MaterialDocumentMaterial(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    document_file = models.FileField(upload_to='course_material_doc/',max_length=1000, verbose_name=_('Document Files'),blank=True,null=True)
    file_name = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("File Name"))
    file_size = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("File Size"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))

    def __str__(self):
        return str(self.document_file)

    class Meta:
        verbose_name_plural = _("Material Document Material")


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
        verbose_name_plural = _("Course Material Status")
    

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
    
    class Meta:
        verbose_name_plural = _("Course Material")


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
        verbose_name_plural = _("Recruitment Ad")
        

class InvoiceData(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    invoice_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Invoice Number'))
    user_address = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('User Address'))
    vat_charges = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Vat'))
    user_email = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    invoice_pdf = models.FileField(blank=True,null=True,upload_to='invoice/',verbose_name=_('Invoice Pdf'))
    course_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Course Name'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))
    

    def __str__(self):
        return str(self.course_name)
    
    class Meta:
        verbose_name_plural = _("Invoice Data")


class InvoiceDataEvent(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    invoice_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Invoice Number'))
    user_address = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('User Address'))
    vat_charges = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Vat'))
    user_email = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    invoice_pdf = models.FileField(blank=True,null=True,upload_to='invoice/',verbose_name=_('Invoice Pdf'))
    event_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Event Name'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))

    def __str__(self):
        return str(self.event_name)
    
    class Meta:
        verbose_name_plural = _("Invoice Data Event")


class EventAdPaymentDetail(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    admin_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Admin Name"))
    event_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event Name"))
    email_id = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    user_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("User Name"))
    card_type = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Card Type"))
    amount = models.FloatField(blank=True,null=True,verbose_name=_("Amount"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Payment Created Date Time'))
    payment_mode = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("Payment Mode"))
    invoice = models.ForeignKey(InvoiceDataEvent, on_delete=models.CASCADE, blank=True,null=True, default=None)
    status = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Payment Status"))
    is_approved = models.ForeignKey(approval_status, on_delete=models.CASCADE, verbose_name=_('Approval Status'), blank=True,null=True, default=None)


    def __str__(self):
        return str(self.event_name)

    class Meta:
        verbose_name_plural = _("Event Ad Payment Detail") 

class EventAdEnroll(models.Model):
    event_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Event name"))
    user_email = models.EmailField(blank=True,null=True,verbose_name=_('User Email'))
    payment_detail = models.ForeignKey(EventAdPaymentDetail,on_delete=models.CASCADE,verbose_name=_('Payment Detail'),blank=True,null=True)
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE,verbose_name=_('User Profile'),blank=True,null=True)
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Created Date Time'))

    def __str__(self):
        return str(self.event_name)

    class Meta:
        verbose_name_plural = _("Event Ad Enroll")
    

class UserPaymentDetail(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'))
    course = models.ForeignKey(CourseDetails, on_delete=models.CASCADE, blank=True,null=True, default=None)
    email_id = models.EmailField(blank=True,null=True,verbose_name=_('Email ID'))
    user_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("User name"))
    card_type = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Card Type"))
    amount = models.FloatField(blank=True,null=True,verbose_name=_("Amount"))
    payment_mode = models.CharField(max_length=500,blank=True,null=True,verbose_name=_("Payment Mode"))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Payment Created Date Time'))
    status = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Payment Status"))
    invoice = models.ForeignKey(InvoiceData, on_delete=models.CASCADE, blank=True,null=True, default=None)
    is_approved = models.ForeignKey(approval_status, on_delete=models.CASCADE, verbose_name=_('Approval Status'), blank=True,null=True, default=None)

    class Meta:
        verbose_name_plural = _("User Payment Detail")

    def __str__(self):
        return str(self.course.course_name)

    
class CourseEnroll(models.Model):
    course_category = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Course Category"))
    supplier_email = models.EmailField(blank=True,null=True,verbose_name=_('supplier email'))
    payment_detail = models.ForeignKey(UserPaymentDetail,on_delete=models.CASCADE,verbose_name=_('Payment Detail'),blank=True,null=True)
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE,verbose_name=_('User Profile'),blank=True,null=True)
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('Favourite Course Created Date Time'))


    def __str__(self):
        return str(self.payment_detail.course.course_name)

    class Meta:
        verbose_name_plural = _("Course Enroll")  

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
        image = 'Logo.png'
        file_path = os.path.join(path,img_dir,image)
        with open(file_path,'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<{name}>'.format(name=image))
            img.add_header('Content-Disposition', 'inline', filename=image)
        email_msg.attach(img)
        email_msg.send(fail_silently=False)
        print("TRUE")

class Notification(models.Model):
    sender = models.TextField(max_length=5000,blank=True,null=True,verbose_name=_('sender'))
    receiver = models.TextField(max_length=5000,blank=True,null=True,verbose_name=_('receiver'))
    user_type = models.ForeignKey(USERSIGNUP_TABLE,on_delete=models.CASCADE,verbose_name=_('User Type'),blank=True,null=True,default=None)
    user_detail = models.ForeignKey(USER_PROFILE_TABLE,on_delete=models.CASCADE,verbose_name=_('User Email'),blank=True,null=True,default=None)
    supplier_detail = models.ForeignKey(SUPPLIER_PROFILE_TABLE,on_delete=models.CASCADE,verbose_name=_('Supplier Email'),blank=True,null=True,default=None)
    message = models.TextField(max_length=2000,blank=True,null=True,verbose_name=_("Address"))
    message_sv = models.TextField(max_length=2000,blank=True,null=True,verbose_name=_("Address"))
    is_clear = models.BooleanField(default=False,verbose_name=_('is_clear'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))

    class Meta:
        verbose_name_plural = _("Notification Table")

class UserDeviceToken(models.Model):
    user_type = models.ForeignKey(USERSIGNUP_TABLE,on_delete=models.CASCADE,verbose_name=_('User Type'),related_name='device_token',blank=True,null=True,default=None)
    device_token = models.CharField(max_length=1000,blank=True,null=True,verbose_name=_('Device Token'))
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name=_('created_date_time'))

    class Meta:
        verbose_name_plural = _("Notification Device Token")

class UserProfileCMS(models.Model):
    user_welcome = models.CharField(max_length=255,blank=True,null=True,verbose_name=_('User Welcome'))
    content = models.TextField(max_length=5000,blank=True,null=True,verbose_name=_('content'))
    button_1_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 1 Text'))
    button_2_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 2 Text'))
    button_3_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 3 Text'))
    button_4_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 4 Text'))

class UserProfileCMS_SV(models.Model):
    user_welcome = models.CharField(max_length=255,blank=True,null=True,verbose_name=_('User Welcome'))
    content = models.TextField(max_length=5000,blank=True,null=True,verbose_name=_('content'))
    button_1_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 1 Text'))
    button_2_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 2 Text'))
    button_3_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 3 Text'))
    button_4_text = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Button 4 Text'))



class PaybyInvoice(models.Model):
    student_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Student Name'))
    dob = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Student DOB'))
    invoice_method = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Invoice Method'))
    personal_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Personal Number'))
    organization_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Organization Name'))
    organization_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Organization Number'))
    street_number = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Street Number'))
    reference = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Reference'))
    zip_code = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Zip'))
    contry = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Contry'))
    city = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('City'))
    # invoice_address = models.CharField(max_length=500,blank=True,null=True,verbose_name=_('Invoice Address'))
    student_email = models.EmailField(max_length=500,null=True,verbose_name=_('Student Email'))
    invoice_email = models.EmailField(max_length=500,null=True,verbose_name=_('Invoice Email'))
    price = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Price'))
    course = models.ForeignKey(CourseDetails,on_delete=models.CASCADE,default=None,null=True,blank=True,verbose_name=_('Course'))
    product_type = models.CharField(max_length=50,blank=True,null=True,verbose_name=_('Product Type'))
    product_name = models.CharField(max_length=500,blank=True,null=True,verbose_name=_('Product Name'))
    payment_mode = models.CharField(max_length=500,blank=True,null=True,verbose_name=_('Payment Mode'))

class SupplierAccountDetail(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    supplier = models.ForeignKey(UserSignup,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('Supplier'))
    commission = models.FloatField(blank=True,null=True,verbose_name=_('Commission'))
    account_id = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Account Id'))
    total_earnings = models.FloatField(blank=True,null=True,verbose_name=_('Total Earnings'))
    total_amount_due = models.FloatField(blank=True,null=True,verbose_name=_('Total Amount Due'))
    total_amount_withdraw = models.FloatField(blank=True,null=True,verbose_name=_('Total Amount Withdraw'))
    created_date_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Created Date Time"))
    modified_date_time = models.DateTimeField(auto_now=True, verbose_name=_("Modified Date Time"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Is Deleted"))
    
    class Meta:
        verbose_name_plural = _("Supplier Account Details Table")

class SupplierPayoutDetail(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    supplier_account = models.ForeignKey(SupplierAccountDetail,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('Supplier Account'))
    payout_id = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Payout Id'))
    amount = models.FloatField(blank=True,null=True,verbose_name=_('Payout Amount'))
    created_date_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Created Date Time"))
    modified_date_time = models.DateTimeField(auto_now=True, verbose_name=_("Modified Date Time"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Is Deleted"))
    
    class Meta:
        verbose_name_plural = _("Supplier Payout Details Table")

class SupplierWithdrawalDetail(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    supplier = models.ForeignKey(SupplierAccountDetail,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('Supplier Account'))
    reason = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Reason'))
    status = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Status'))
    amount = models.FloatField(blank=True,null=True,verbose_name=_('Payout Amount'))
    created_date_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Created Date Time"))
    modified_date_time = models.DateTimeField(auto_now=True, verbose_name=_("Modified Date Time"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Is Deleted"))
    
    class Meta:
        verbose_name_plural = _("Supplier Withdrawal Details Table")

class CourseBatch(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    batch_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Batch Name'))
    course = models.ForeignKey(CourseDetails,on_delete=models.CASCADE,blank=True,null=True,verbose_name=_("Course"))
    students = models.ManyToManyField(UserProfile,blank=True,null=True,verbose_name=_('Students'))
    created_by = models.CharField(max_length=100,blank=True, verbose_name=_("Created By"))
    modified_by = models.CharField(max_length=100,blank=True, verbose_name=_("Modified By"))
    created_date_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Created Date Time"))
    modified_date_time = models.DateTimeField(auto_now=True, verbose_name=_("Modified Date Time"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Is Deleted"))
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name=_("Status"),blank=True,null=True)

    class Meta:
        verbose_name_plural = _("Course Batch Table")

   
class BatchSession(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name=_('UUID'),blank=True,null=True)
    session_name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Session Name'))
    batch = models.ForeignKey(CourseBatch, on_delete=models.CASCADE,blank=True,null=True,verbose_name=_('Batch'))
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(verbose_name=_('Session Start Time'))
    end_time = models.TimeField(verbose_name=_('Session End Time'))
    total_duration = models.CharField(max_length=100,verbose_name=_('Total Duration'))
    url = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Session Url'))
    event_id = models.CharField(max_length=100,blank=True,null=True,verbose_name=_('Event Id'))
    choose_days = models.CharField(max_length=100,null=True,verbose_name=_('Choose Day'))
    customDays = models.CharField(max_length=100,null=True,verbose_name=_('Custom Days'))
    created_by = models.CharField(max_length=100,blank=True, verbose_name=_("Created By"))
    modified_by = models.CharField(max_length=100,blank=True, verbose_name=_("Modified By"))
    created_date_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Created Date Time"))
    modified_date_time = models.DateTimeField(auto_now=True, verbose_name=_("Modified Date Time"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Is Deleted"))
    
    class Meta:
        verbose_name_plural = _("Batch Session Table")

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
        context_data = {'final_otp':otp,'fullname':fullname, "email":instance.email_id,"url":SUPPLIER_URL,"user_type":"admin"}
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
        context_data = {'final_otp':otp,'fullname':fullname, "email":instance.email_id, "url":SUPPLIER_URL,"user_type":"supplier"}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
        data = UserSignup.objects.get(email_id = instance.email_id)
        data.password = make_password(otp)
        data.save()
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

    if created and instance.user_type.user_type == 'User':
        html_path = VERIFY_EMAIL
        fullname = f'{instance.first_name} {instance.last_name}'
        context_data = {'fullname':fullname,"url":FRONT_URL+f"verify-user/{instance.uuid}"}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
        email_msg = EmailMessage('Please verify your Eddi account',email_html_template,email_from,recipient_list)
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
        context_data = {'fullname':fullname, "email":student.email_id,"session_name":instance.session_name}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (student.email_id,)
        email_msg = EmailMessage('Invitation To Join Session',email_html_template,email_from,recipient_list)
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

