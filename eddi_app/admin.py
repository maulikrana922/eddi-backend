import imp
from django.contrib import admin
from .models import *

admin.site.register(utl_status)
admin.site.register(UserSignup)
admin.site.register(CourseCategoryDetails)
admin.site.register(CourseType)
admin.site.register(CourseLevel)
admin.site.register(FeeType)
admin.site.register(CourseDetails)
admin.site.register(CourseSubCategoryDetails)
admin.site.register(approval_status)
admin.site.register(UserType)



admin.site.site_header = 'Eddi Admin'