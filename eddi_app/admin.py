import imp
from django.contrib import admin
from .models import *
from  django.contrib.auth.models  import  Group 

admin.site.register(utl_status)

admin.site.register(CourseCategoryDetails)
admin.site.register(CourseType)
admin.site.register(CourseLevel)
admin.site.register(FeeType)
admin.site.register(CourseDetails)
admin.site.register(CourseSubCategoryDetails)
admin.site.register(approval_status)
admin.site.register(UserType)

admin.site.unregister(Group)
# admin.site.register(HomePageCMSBanner)


class HomePageCMSBannerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('image_title','banner',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )


admin.site.register(HomePageCMSBanner,HomePageCMSBannerAdmin)

class BlogDetailsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('blog_image','blog_title','blog_description','written_by')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )


admin.site.register(BlogDetails,BlogDetailsAdmin)

class HomePageCMSPartnersAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('image_title','partner_logo',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )


admin.site.register(HomePageCMSPartners,HomePageCMSPartnersAdmin)

class TestinomialsDetailsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('user_id','review',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )


admin.site.register(TestinomialsDetails,TestinomialsDetailsAdmin)
class AboutUsPageCMSAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - How It Works', {
            'classes': ('collapse',),
            'fields': ('section_2_heading','section_2_description','section_2_video'),
        }),
         ('Section 3 - Why Eddi', {
            'classes': ('collapse',),
            'fields': ('section_3_heading','section_3_image','section_3_description','section_3_button_text','section_3_button_link',),
        }),
        ('Section 4 - Our Newest Courses', {
            'classes': ('collapse',),
            'fields': ('section_4_heading','section_4_courses','section_4_button_text','section_4_button_link'),
        }),
    )
   

admin.site.register(AboutUsPageCMS, AboutUsPageCMSAdmin)
class HomePageCMSAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_description','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - About Eddi', {
            'classes': ('collapse',),
            'fields': ('section_2_heading','section_2_description','section_2_left_button_text','section_2_left_button_link','section_2_right_button_text','section_2_right_button_link'),
        }),
         ('Section 3 - Courses Eddi Offers', {
            'classes': ('collapse',),
            'fields': ('section_3_heading','section_3_button_text','section_3_button_link',),
        }),
        ('Section 4 - Eddi Partners', {
            'classes': ('collapse',),
            'fields': ('section_4_heading','section_4_logo',),
        }),
        ('Section 5 - News and Articles', {
            'classes': ('collapse',),
            'fields': ('section_5_heading','section_5_blog',),
        }),
        ('Section 6 - Testinomials', {
            'classes': ('collapse',),
            'fields': ('section_6_heading','section_6_description','section_6_testinomials',),
        }),
        ('Section 8 - Become Supplier', {
            'classes': ('collapse',),
            'fields': ('section_8_heading','section_8_image','section_8_description','section_8_button_text','section_8_button_link'),
        }),
    )
   

admin.site.register(HomePageCMS, HomePageCMSAdmin)




class UserSignupAdmin(admin.ModelAdmin):
    list_display = ('email_id','user_type','status')

    list_filter = ('user_type','status')

# class  authorAdmin(admin.ModelAdmin):
#     list_display=['image_tag','category_name']


# admin.site.register(CourseCategoryDetails,authorAdmin)


admin.site.register(UserSignup, UserSignupAdmin)
admin.site.site_header = 'Eddi Admin'

#    fieldsets = (
#         ('Section 1', {
#             'fields': ('email_id','user_type',)
#         }),
#         ('Section 2', {
#             'classes': ('collapse',),
#             'fields': ('status',),
#         }),
#     )