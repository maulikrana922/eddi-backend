from django.db import models
import uuid
from django.conf import settings
from django.core.mail import EmailMessage

from django.db.models.signals import post_save
from django.dispatch import receiver
import string
import random
from django.template.loader import get_template

from eddi_app.constants.constants import OTP_EMAIL_HTML
from django.contrib.auth.hashers import make_password, check_password



otp = ''


# Create your models here.
def PasswordView():
    global otp
    context = None
    digits = "" + str(string.ascii_letters) + str(string.digits) + "!@#$%^&*()"
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
    status = models.ManyToManyField(utl_status,null=True,blank=True)
    value = models.CharField(max_length=60,blank=True)

    created_by = models.CharField(max_length=100,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100,blank=True)
    modified_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Approval Status Table"

    def __str__(self):
        return self.value

class UserSignup(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True)
    email_id = models.EmailField(unique=True)
    password = models.CharField(max_length=150,blank=True,null=True,)

    user_type = models.ForeignKey(UserType,on_delete=models.CASCADE,blank=True,null=True,verbose_name="User Type")
    is_first_time_login = models.BooleanField(default=True)


    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    class Meta:
        verbose_name = "User Signup Table"

    def __str__(self):
        return self.email_id

@receiver(post_save, sender=UserSignup)
def send_appointment_confirmation_email(sender, instance, created, **kwargs):
  if created:
      if instance.user_type.user_type == 'Supplier':
            html_path = OTP_EMAIL_HTML
            otp = PasswordView()
            context_data = {'final_otp':otp}
            email_html_template = get_template(html_path).render(context_data)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = (instance.email_id,)
            data = UserSignup.objects.get(email_id = instance.email_id)
            data.password = make_password(otp)
            data.save()
            email_msg = EmailMessage('Welcome to Eddi',email_html_template,email_from,recipient_list)
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)

class CourseCategoryDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name='UUID',blank=True,null=True)
    category_name = models.CharField(max_length=150,verbose_name='Category Name',blank=True,null=True)
    category_image = models.FileField(upload_to='category_image/',verbose_name='Category Image',blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')


    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    class Meta:
        verbose_name = "Course Category Table"

    def __str__(self):
        return self.category_name

class CourseSubCategoryDetails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,verbose_name='UUID',blank=True,null=True)
    category_name = models.ForeignKey(CourseCategoryDetails,on_delete=models.CASCADE,verbose_name='Category Name',blank=True,null=True)
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
    supplier = models.ForeignKey(UserSignup,on_delete=models.CASCADE,limit_choices_to={'is_supplier': True})
    course_image = models.FileField(upload_to='course_image/',verbose_name='Course Image',blank=True,null=True)
    course_name = models.CharField(max_length=150,verbose_name='Course Name',blank=True,null=True)
    course_level = models.ForeignKey(CourseLevel,on_delete=models.CASCADE,verbose_name='Course Level',blank=True,null=True)
    course_length = models.IntegerField(default=0,verbose_name='Course Length',blank=True,null=True)
    course_category = models.ForeignKey(CourseCategoryDetails,on_delete=models.CASCADE,verbose_name='Course Category',blank=True,null=True)
    course_subcategory = models.ForeignKey(CourseSubCategoryDetails,on_delete=models.CASCADE,verbose_name='Course Category',blank=True,null=True)

    course_type = models.ForeignKey(CourseType,on_delete=models.CASCADE,verbose_name='Course Type',blank=True,null=True)
    fee_type = models.ForeignKey(FeeType,on_delete=models.CASCADE,verbose_name='Fee Type',blank=True,null=True)
    course_price = models.FloatField(default=0,verbose_name='Course Price',blank=True,null=True)
    additional_information = models.TextField(max_length=1500,verbose_name='Additional Information',blank=True,null=True)
    organization_location = models.CharField(max_length=500,verbose_name='Organization Location',blank=True,null=True)
    sub_area = models.CharField(max_length=300,verbose_name='Sub Area',blank=True,null=True)

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



