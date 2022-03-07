from django.db import models
import uuid

# Create your models here.
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



class UserSignup(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True)
    email_id = models.EmailField(unique=True)
    password = models.CharField(max_length=150)

    is_student = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_first_time_login = models.BooleanField(default=False)


    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    class Meta:
        verbose_name = "User Signup Table"

    def __str__(self):
        return self.email_id



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
    course_type = models.ForeignKey(CourseType,on_delete=models.CASCADE,verbose_name='Course Type',blank=True,null=True)
    fee_type = models.ForeignKey(FeeType,on_delete=models.CASCADE,verbose_name='Fee Type',blank=True,null=True)
    course_price = models.IntegerField(default=0,verbose_name='Course Price',blank=True,null=True)
    additional_information = models.TextField(max_length=1500,verbose_name='Additional Information',blank=True,null=True)

    created_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Created By')
    created_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Created Date Time')
    modified_by = models.CharField(max_length=100,blank=True,null=True,verbose_name='Modified By')
    modified_date_time = models.DateTimeField(auto_now_add=True,verbose_name='Modified Date Time')

    status = models.ForeignKey(utl_status,on_delete=models.CASCADE,verbose_name='Status',blank=True,null=True)

    class Meta:
        verbose_name = "Course Details Table"

    def __str__(self):
        return self.course_name



