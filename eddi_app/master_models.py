from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

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
    