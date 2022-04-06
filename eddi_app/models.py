from distutils.command.upload import upload
from tabnanny import verbose
from django.forms import CharField
from django.utils.safestring import mark_safe
from django.db import models
import uuid
from django.conf import settings
from django.core.mail import EmailMessage

from django.db.models.signals import post_save
from django.dispatch import receiver
import string
import random
from django.template.loader import get_template
from ckeditor.fields import RichTextField
from eddi_app.constants.constants import *
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework.authtoken.models import Token



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
    value = models.CharField(max_length=60,blank=True)

    created_by = models.CharField(max_length=100,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100,blank=True)
    modified_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Status Table"

    def __str__(self):
        return self.value

class UserType(models.Model):
    user_type = models.CharField(max_length=60,blank=True, verbose_name="User Type")

    created_by = models.CharField(max_length=100,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100,blank=True)
    modified_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Type Table"

    def __str__(self):
        return self.user_type


class approval_status(models.Model):
    status = models.ManyToManyField(utl_status,null=True,blank=True, verbose_name='Status')
    value = models.CharField(max_length=60,blank=True)
    created_by = models.CharField(max_length=100,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100,blank=True)
    modified_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Approval Status Table'

    def __str__(self):
        return self.value

class UserSignup(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True)
    first_name = models.CharField(max_length=150, blank=True, null=True, verbose_name='First Name')
    last_name = models.CharField(max_length=150, blank=True, null=True, verbose_name='Last Name')
    password = models.CharField(max_length=150,blank=True,null=True,)
    email_id = models.EmailField(unique=True)
    password = models.CharField(max_length=150,blank=True,null=True,)

    user_type = models.ForeignKey(UserType,on_delete=models.CASCADE,blank=True,null=True,verbose_name="User Type")
    is_first_time_login = models.BooleanField(default=True)


    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')
    is_authenticated = models.BooleanField(default=False)

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True,default=1)



@receiver(post_save, sender=UserSignup)
def send_appointment_confirmation_email(sender, instance, created, **kwargs):
    print("OUTER")
    if created and instance.user_type.user_type == SUPPLIER_S or instance.user_type.user_type == ADMIN_S:
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
        email_msg.send(fail_silently=False)
        print("TRUE")
    
    if created and instance.user_type.user_type == 'User':
        print("User")

        html_path = USER_WELCOME_HTML
        fullname = f'{instance.first_name} {instance.last_name}'
        context_data = {'fullname':fullname}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (instance.email_id,)
        email_msg = EmailMessage('Welcome to Eddi',email_html_template,email_from,recipient_list)
        email_msg.content_subtype = 'html'
        print("TRUE")
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
            verbose_name=("email_id")
        )



class CourseCategoryDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name='UUID',blank=True,null=True)
    category_name = models.CharField(max_length=150,verbose_name='Category Name',blank=True,null=True)
    category_image = models.FileField(upload_to='category_image/',verbose_name='Category Image',blank=True,null=True)
    color = models.CharField(max_length=100,blank=True,null=True,verbose_name='Color')

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')


    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    # def  image_tag(self):
    #     return mark_safe('<img src="/../../media/%s" width="150" height="150" />' % (self.category_image))

    # image_tag.allow_tags = True

    class Meta:
        verbose_name = "Course Category Table"

    def __str__(self):
        return self.category_name

class CourseSubCategoryDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name='UUID',blank=True,null=True)
    category_name = models.ForeignKey(CourseCategoryDetails,on_delete=models.CASCADE,verbose_name='Sub Category Name',blank=True,null=True)
    supplier = models.ForeignKey(UserSignup,on_delete=models.CASCADE,null=True,blank=True,limit_choices_to={'user_type_id': 1})

    subcategory_name = models.CharField(max_length=150,verbose_name='Category Name',blank=True,null=True)

    subcategory_image = models.FileField(upload_to='category_image/',verbose_name='Category Image',blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    is_approved = models.ForeignKey(approval_status,on_delete=models.CASCADE,blank=True,null=True)
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    class Meta:
        verbose_name = "Course Sub Category Table"

    def __str__(self):
        return self.subcategory_name


class CourseType(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name='UUID',blank=True,null=True)
    type_name = models.CharField(max_length=150,verbose_name='Course Type Name',blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    class Meta:
        verbose_name = "Course Type Table"

    def __str__(self):
        return self.type_name

class CourseLevel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name='UUID',blank=True,null=True)
    level_name = models.CharField(max_length=150,verbose_name='Course Level Name',blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    class Meta:
        verbose_name = "Course Level Table"

    def __str__(self):
        return self.level_name

class FeeType(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name='UUID',blank=True,null=True)
    fee_type_name = models.CharField(max_length=150,verbose_name='Fee Type Name',blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    class Meta:
        verbose_name = "Fee Type Table"

    def __str__(self):
        return self.fee_type_name

class CourseDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name='UUID',blank=True,null=True)
    supplier = models.ForeignKey(UserSignup,on_delete=models.CASCADE,blank=True,null=True)
    course_image = models.FileField(upload_to='course_image/',verbose_name='Course Image',blank=True,null=True)
    course_name = models.CharField(max_length=150,verbose_name='Course Name',blank=True,null=True)
    course_level = models.ForeignKey(CourseLevel,on_delete=models.CASCADE,verbose_name='Course Level',blank=True,null=True)
    course_length = models.IntegerField(default=0,verbose_name='Course Length',blank=True,null=True)
    course_category = models.ForeignKey(CourseCategoryDetails,on_delete=models.CASCADE,verbose_name='Course Category',blank=True,null=True)
    course_subcategory = models.ForeignKey(CourseSubCategoryDetails,on_delete=models.CASCADE,verbose_name='Course Category',blank=True,null=True)
    course_language = models.CharField(max_length=100,blank=True,null=True)

    course_for_organization = models.BooleanField(default=False)
    organization_domain = models.CharField(max_length=100,blank=True,null=True)
    course_type = models.ForeignKey(CourseType,on_delete=models.CASCADE,verbose_name='Course Type',blank=True,null=True)
    fee_type = models.ForeignKey(FeeType,on_delete=models.CASCADE,verbose_name='Fee Type',blank=True,null=True)
    course_price = models.FloatField(default=0,verbose_name='Course Price',blank=True,null=True)
    additional_information = models.TextField(max_length=1500,verbose_name='Additional Information',blank=True,null=True)
    organization_location = models.CharField(max_length=500,verbose_name='Organization Location',blank=True,null=True)
    sub_area = models.CharField(max_length=300,verbose_name='Sub Area',blank=True,null=True)
    course_checkout_link = models.CharField(max_length=255,verbose_name='Checkout Link',blank=True,null=True)
    

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    is_approved = models.ForeignKey(approval_status,on_delete=models.CASCADE,blank=True,null=True)
    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    class Meta:
        verbose_name = "Course Details Table"

    def __str__(self):
        return self.course_name
    
@receiver(post_save, sender=CourseDetails)
def add_organization_domain(sender, instance, created, **kwargs):
    if created and instance.course_for_organization == True:
        
        test_str = instance.supplier.email_id
        res = test_str.split('@')[1]
        print(res)
        CourseDetails.objects.filter(uuid = instance.uuid).update(organization_domain = str(res))

       

################## CMS    ###################################
class HomePageCMSBanner(models.Model):
    image_title = models.CharField(max_length=50,blank=True,null=True)
    banner = models.ImageField(upload_to = 'homepage_banner/', verbose_name="Banner Image")

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

class HomePageCMSPartners(models.Model):
    image_title = models.CharField(max_length=50,blank=True,null=True)
    partner_logo = models.ImageField(upload_to = 'homepage_partner_logo/', verbose_name="Partner Logo")

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    def __str__(self):
        return str(self.partner_logo.url)

class ContactFormLead(models.Model):
    fullname = models.CharField(max_length=100,blank=True,null=True,verbose_name='Full Name')
    email_id = models.EmailField(blank=True,null=True,verbose_name='Email ID')
    phone_number = models.BigIntegerField(blank=True,null=True,verbose_name='Phone Number')
    message = models.TextField(max_length=500,blank=True,null=True,verbose_name='Message')

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    def __str__(self):
        return self.email_id

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
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name='UUID',blank=True,null=True)

    blog_image = models.ImageField(upload_to = 'blog_image/', verbose_name="Blog Image")
    blog_title = models.CharField(max_length=500,null=True,blank=True,verbose_name='Blog Title')
    blog_description = RichTextField(verbose_name = 'Blog Description',blank = True)
    blog_category = models.ForeignKey(CourseCategoryDetails,on_delete=models.CASCADE,null=True,blank=True,verbose_name="Blog Category")
    written_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Written by')

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)


    class Meta:
        verbose_name = "Blog Table"

class TestinomialsDetails(models.Model):
    user_id = models.ForeignKey(UserSignup,on_delete=models.CASCADE,null=True,blank=True,verbose_name='User Details')
    review = RichTextField(blank=True,verbose_name = 'User Review')
    # profile_image = models.ImageField(upload_to = 'blog_image/', blank=True,null=True,verbose_name="Profile Image")
    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)







class HomePageCMS(models.Model):

    #section 1
    section_1_image = models.ManyToManyField(HomePageCMSBanner,blank=True,null=True,verbose_name='Banner Image')
    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")


    section_1_description = RichTextField(verbose_name = 'Description',blank=True)


    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Button Text')
    section_1_button_link = models.URLField(verbose_name='Button URL',blank=True,null=True)

    #section 2
    section_2_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_2_description = RichTextField(verbose_name = 'Description',blank=True)
    section_2_left_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Left Button Text')
    section_2_left_button_link = models.URLField(verbose_name='Left Button URL',blank=True,null=True)
    section_2_right_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Right Button Text')
    section_2_right_button_link = models.URLField(verbose_name='Right Button URL',blank=True,null=True)

    #section 3
    section_3_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_3_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Button Text')
    section_3_button_link = models.URLField(verbose_name='Button URL',blank=True,null=True)

    #section 4
    section_4_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_4_logo = models.ManyToManyField(HomePageCMSPartners,verbose_name='Partner Logo',blank=True,null=True)

    #section 5
    section_5_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_5_blog = models.ManyToManyField(BlogDetails,blank=True,null=True,verbose_name="Blog")

    #section 6
    section_6_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_6_description = models.CharField(max_length=80,blank=True,null=True,verbose_name="Description")
    section_6_testinomials = models.ManyToManyField(TestinomialsDetails,blank=True,null=True,verbose_name='Testinomials')

    #section 8
    section_8_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_8_image = models.ImageField(upload_to = 'homepage/',blank=True,null=True,verbose_name='Image')
    section_8_description = RichTextField(verbose_name = 'Description',blank=True)
    section_8_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Button Text')
    section_8_button_link = models.URLField(verbose_name='Button URL',blank=True,null=True)
   
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')




    class Meta:
        verbose_name = "Home Page"

def regions_changed(sender, **kwargs):
    if kwargs['instance'].section_5_blog.count() > 4:
        raise ValidationError("You can't assign more than four regions")

m2m_changed.connect(regions_changed, sender=HomePageCMS.section_5_blog.through)


class AboutUsPageCMS(models.Model):

    #section 1
    section_1_image = models.ImageField(upload_to = 'about_us/',blank=True,null=True,verbose_name='Banner Image')
    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Button Text')
    section_1_button_link = models.URLField(verbose_name='Button URL',blank=True,null=True)

    #section 2
    section_2_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_2_description = RichTextField(verbose_name = 'Description',blank=True)
    section_2_video = models.FileField(verbose_name='Video Upload',upload_to='about_us/',null=True,blank=True)

    #section 3
    section_3_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_3_image = models.ImageField(upload_to = 'about_us/',blank=True,null=True,verbose_name='Image')
    section_3_description = RichTextField(verbose_name = 'Description',blank=True)
    section_3_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Button Text')
    section_3_button_link = models.URLField(verbose_name='Button URL',blank=True,null=True)

    #section 4
    section_4_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_4_courses = models.ManyToManyField(CourseDetails,verbose_name='Newest Courses',blank=True,null=True)
    section_4_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Button Text')
    section_4_button_link = models.URLField(verbose_name='Button URL',blank=True,null=True)

   
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    class Meta:
        verbose_name = "About Us Page"


class ContactUsPageCMS(models.Model):
    
    #section 1
    section_1_image = models.ImageField(upload_to = 'about_us/',blank=True,null=True,verbose_name='Banner Image')
    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Button Text')
    section_1_button_link = models.URLField(verbose_name='Button URL',blank=True,null=True)

    #section 2
    section_2_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_2_address = models.CharField(max_length=80,blank=True,null=True,verbose_name="Address")
    section_2_contact = models.CharField(max_length=80,blank=True,null=True,verbose_name="Contact Number")
    section_2_email = models.EmailField(blank=True,null=True,verbose_name="Email ID")

    section_2_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Button Text')

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    class Meta:
        verbose_name = "Contact Us Page"


class PrivacyPolicyCMS(models.Model):
    #section 1
    section_1_image = models.ImageField(upload_to = 'privacy_policy/',blank=True,null=True,verbose_name='Banner Image')
    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Button Text')
    section_1_button_link = models.URLField(verbose_name='Button URL',blank=True,null=True)

    #section 2
    section_2_main_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Main Heading")
    section_2_left_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Left Heading")
    section_2_description = RichTextField(verbose_name = 'Description',blank=True)
    section_2_sub_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Sub Heading")
    section_2_sub_description = RichTextField(verbose_name = 'Sub Description',blank=True)
    section_2_last_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Last Heading")
    section_2_last_description = RichTextField(verbose_name = 'Last Description',blank=True)

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    class Meta:
        verbose_name = "Privacy Policy Page"

class TermsConditionCMS(models.Model):
    #section 1
    section_1_image = models.ImageField(upload_to = 'terms_conditon/',blank=True,null=True,verbose_name='Banner Image')

    section_1_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Heading")
    section_1_button_text = models.CharField(max_length=50,blank=True,null=True,verbose_name='Button Text')
    section_1_button_link = models.URLField(verbose_name='Button URL',blank=True,null=True)
    #section 2
    section_2_main_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Main Heading")
    section_2_left_heading = models.CharField(max_length=80,blank=True,null=True,verbose_name="Left Heading")
    section_2_description = RichTextField(verbose_name = 'Description',blank=True)

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    class Meta:
        verbose_name = "Terms & Condition Page"



class UserProfile(models.Model):
    email_id = models.CharField(max_length=255,blank=True,null=True,verbose_name="Email Id",unique=True)

    #personal information
    profile_image = models.ImageField(upload_to = 'profile_image/',blank=True,null=True,verbose_name='Profile Image')
    first_name = models.CharField(max_length=50,blank=True,null=True,verbose_name="First Name")
    last_name = models.CharField(max_length=50,blank=True,null=True,verbose_name="Last Name")
    gender = models.CharField(max_length=50,blank=True,null=True,verbose_name="Gender")
    dob = models.CharField(max_length=50,blank=True,null=True,verbose_name="Date of Birth")
    personal_number = models.IntegerField(blank=True,null=True,verbose_name="Personal Number")
    phone_number = models.BigIntegerField(blank=True,null=True,verbose_name="Phone Number")

    #Educational Information
    highest_education = models.CharField(max_length=50,blank=True,null=True,verbose_name="Highest Level of Education")
    university_name = models.CharField(max_length=50,blank=True,null=True,verbose_name="University Name")
    highest_degree = models.CharField(max_length=50,blank=True,null=True,verbose_name="Highest Degree")
    educational_area = models.CharField(max_length=50,blank=True,null=True,verbose_name="Educational Area")
    other_education = models.CharField(max_length=50,blank=True,null=True,verbose_name="Other Relavant Education")
    diplomas_certificates = models.CharField(max_length=50,blank=True,null=True,verbose_name="Diplomas and Certificates")

    #Professional Information
    current_professional_role = models.CharField(max_length=50,blank=True,null=True,verbose_name="Current Professional Role")
    additional_role = models.CharField(max_length=50,blank=True,null=True,verbose_name="Additional Role")
    extra_curricular = models.CharField(max_length=100,blank=True,null=True,verbose_name="Extra Curricular You Want")
    extra_curricular_competence = models.CharField(max_length=100,blank=True,null=True,verbose_name="Extra Curricular Competence You Have")
    core_responsibilities = models.CharField(max_length=100,blank=True,null=True,verbose_name="Core Responsibilities")
    level_of_role = models.CharField(max_length=100,blank=True,null=True,verbose_name="Level Of Role")
    future_professional_role = models.CharField(max_length=100,blank=True,null=True,verbose_name="Future Professional Role")

    #area of interest
    course_category = models.CharField(max_length=100,blank=True,null=True,verbose_name="Course Categories")
    area_of_interest = models.CharField(max_length=100,blank=True,null=True,verbose_name="Area of Interest")
    agree_ads_terms = models.BooleanField(default=True)

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    class Meta:
        verbose_name = "User Profile Table"


    def __str__(self):
        return self.email_id
    



class UserPaymentDetail(models.Model):
    course_name = models.CharField(max_length=100,blank=True,null=True,verbose_name="Course name")
    email_id = models.EmailField(blank=True,null=True,verbose_name='Email ID')
    card_type = models.CharField(max_length=100,blank=True,null=True,verbose_name="Card Type")
    amount = models.FloatField(blank=True,null=True,verbose_name="Amount")
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Payment Created Date Time')
    status = models.CharField(max_length=100,blank=True,null=True,verbose_name="Payment Status")







class FavouriteCourse(models.Model):
    course_name = models.CharField(max_length=100,blank=True,null=True,verbose_name="Course Name")
    email_id = models.EmailField(blank=True,null=True,verbose_name='Email ID')
    is_favourite = models.BooleanField(default=False)
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Favourite Course Created Date Time')
    
    def __str__(self):
        return self.course_name
    


class CourseEnroll(models.Model):
    course_category = models.CharField(max_length=100,blank=True,null=True,verbose_name="Course Category")
    supplier_email = models.EmailField(blank=True,null=True,verbose_name='supplier email')
    payment_detail = models.ForeignKey(UserPaymentDetail,on_delete=models.CASCADE,verbose_name='Payment Detail',blank=True,null=True)
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE,verbose_name='User Profile',blank=True,null=True)
    
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Favourite Course Created Date Time')


    def __str__(self):
        return self.payment_detail.course_name
  
    
    

class EventAd(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True)
    event_image = models.FileField(upload_to='event_image/',verbose_name='Event Image',blank=True,null=True)
    event_publish_on = models.CharField(max_length=100,blank=True,null=True,verbose_name="Publish on")
    event_name = models.CharField(max_length=100,blank=True,null=True,verbose_name="Event Name")
    event_category = models.CharField(max_length=100,blank=True,null=True,verbose_name="Event Category")
    banner_video_link =  models.CharField(max_length=100,blank=True,null=True,verbose_name="Event Banner Link")
    start_date = models.DateTimeField(verbose_name='Event Start Date', blank=True,null=True)
    start_time = models.TimeField(verbose_name='Event Start Time', blank=True,null=True)
    fees_type = models.CharField(max_length=100,blank=True,null=True,verbose_name="Fees Type")
    event_type = models.CharField(max_length=100,blank=True,null=True,verbose_name="Event Type")
    event_price = models.FloatField(default=0,verbose_name='Event Price',blank=True,null=True)
    checkout_link =  models.CharField(max_length=100,blank=True,null=True,verbose_name="Checkout Link")
    event_small_description = RichTextField(verbose_name = 'Event Small Description', blank = True, null=True)
    event_description = RichTextField(verbose_name = 'Event Description', blank = True, null=True)
    event_location = models.CharField(max_length=500,blank=True,null=True,verbose_name="Location")
    event_organizer = models.CharField(max_length=100,blank=True,null=True,verbose_name="Organizer")
    event_subscriber = models.IntegerField(default=0,verbose_name='Course Subscriber',blank=True,null=True)
    is_featured = models.BooleanField(default=False)

    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Favourite Course Created Date Time')

    def __str__(self):
        return self.event_name