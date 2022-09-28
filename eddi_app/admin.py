from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import *
from .master_models import *
from  django.contrib.auth.models  import  Group 
from .forms import CategoryForm

admin.site.register(utl_status)

class CourseCategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ('category_name','category_image','color')
admin.site.register(CourseCategoryDetails,CourseCategoryAdmin)
admin.site.register(CourseType)
admin.site.register(CourseLevel)
admin.site.register(FeeType)

admin.site.register(SupplierOrganizationProfile)
admin.site.register(SupplierProfile)


admin.site.register(CourseDetails)
admin.site.register(CourseSubCategoryDetails)
admin.site.register(approval_status)
admin.site.register(UserType)
admin.site.register(UserDeviceToken)


admin.site.unregister(Group)
# admin.site.register(HomePageCMSBanner)


class HomePageCMSBannerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('image_title','banner','description', 'button_text', 'button_link')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )


admin.site.register(HomePageCMSBanner,HomePageCMSBannerAdmin)

class HomePageCMSBanner_SVAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('image_title','banner','description', 'button_text', 'button_link')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )


admin.site.register(HomePageCMSBanner_SV,HomePageCMSBanner_SVAdmin)
admin.site.register(InvoiceVATCMS)

class BlogDetailsAdmin(admin.ModelAdmin):
    list_display = ('blog_title','written_by')
    list_filter = ('written_by',)

    fieldsets = (
        (None, {
            'fields': ('blog_image','blog_title','blog_description','blog_category','written_by')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )

admin.site.register(BlogDetails,BlogDetailsAdmin)

class BlogDetails_SVAdmin(admin.ModelAdmin):
    list_display = ('blog_title','written_by')
    list_filter = ('written_by',)

    fieldsets = (
        (None, {
            'fields': ('blog_image','blog_title','blog_description','blog_category','written_by')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )


admin.site.register(BlogDetails_SV,BlogDetails_SVAdmin)

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

class HomePageCMSPartners_SVAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('image_title','partner_logo',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )

admin.site.register(HomePageCMSPartners_SV,HomePageCMSPartners_SVAdmin)

class TestinomialsDetailsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('user_id','review','profile_image','user_name')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )


admin.site.register(TestinomialsDetails,TestinomialsDetailsAdmin)

class TestinomialsDetails_SVAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('user_id','review','profile_image','user_name')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('created_by','modified_by',)
        }),

    )


admin.site.register(TestinomialsDetails_SV,TestinomialsDetails_SVAdmin)

class AboutUsPageCMSAdmin(admin.ModelAdmin):
    
       fieldsets = (
        (_('Section 1 - Main'), {
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


class AboutUsPageCMS_SVAdmin(admin.ModelAdmin):
    
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
   

admin.site.register(AboutUsPageCMS_SV, AboutUsPageCMS_SVAdmin)

class HomePageCMSAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image',)
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

class HomePageCMS_SVAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image',)
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
   

admin.site.register(HomePageCMS_SV, HomePageCMS_SVAdmin)

class ContactUsPageCMSAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - Get In Touch', {
            'classes': ('collapse',),
            'fields': ('section_2_heading','section_2_address','section_2_contact','section_2_email','section_2_latitude', 'section_2_longitude', 'section_2_button_text'),
        }),
       )

admin.site.register(ContactUsPageCMS, ContactUsPageCMSAdmin)

class ContactUsPageCMS_SVAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - Get In Touch', {
            'classes': ('collapse',),
            'fields': ('section_2_heading','section_2_address','section_2_contact','section_2_email','section_2_latitude', 'section_2_longitude', 'section_2_button_text'),
        }),
       )

admin.site.register(ContactUsPageCMS_SV, ContactUsPageCMS_SVAdmin)


class Header_FooterCMSAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Header', {
            'classes': ('collapse',),
            'fields': ('eddi_logo_header','button_1_text','button_2_text','button_3_text','button_4_text','login_button_text')
        }),
        ('Footer', {
            'classes': ('collapse',),
            'fields': ('eddi_logo_footer','description','follow_us_text','social_media_icon1','social_media_icon2','social_media_icon3','copyright_text','quick_link_text','quick_link_button_text1','quick_link_button_text2','quick_link_button_text3','quick_link_button_text4','quick_link_button_text5','quick_link_button_text6'),
        }),
       )

admin.site.register(Header_FooterCMS, Header_FooterCMSAdmin)

class Header_FooterCMS_SVAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Header', {
            'classes': ('collapse',),
            'fields': ('eddi_logo_header','button_1_text','button_2_text','button_3_text','button_4_text','login_button_text')
        }),
        ('Footer', {
            'classes': ('collapse',),
            'fields': ('eddi_logo_footer','description','follow_us_text','social_media_icon1','social_media_icon2','social_media_icon3','copyright_text','quick_link_text','quick_link_button_text1','quick_link_button_text2','quick_link_button_text3','quick_link_button_text4','quick_link_button_text5','quick_link_button_text6'),
        }),
       )

admin.site.register(Header_FooterCMS_SV, Header_FooterCMS_SVAdmin)

class PrivacyPolicyCMSAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - Privacy Policy', {
            'classes': ('collapse',),
            'fields': ('section_2_main_heading','section_2_left_heading','section_2_description','section_2_sub_heading','section_2_sub_description','section_2_last_heading','section_2_last_description'),
        })
    )
   

admin.site.register(PrivacyPolicyCMS, PrivacyPolicyCMSAdmin)

class PrivacyPolicyCMS_SVAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - Privacy Policy', {
            'classes': ('collapse',),
            'fields': ('section_2_main_heading','section_2_left_heading','section_2_description','section_2_sub_heading','section_2_sub_description','section_2_last_heading','section_2_last_description'),
        })
    )
   
admin.site.register(PrivacyPolicyCMS_SV, PrivacyPolicyCMS_SVAdmin)

class PrivacyPolicyCMSSupplierAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - Privacy Policy', {
            'classes': ('collapse',),
            'fields': ('section_2_main_heading','section_2_left_heading','section_2_description','section_2_sub_heading','section_2_sub_description','section_2_last_heading','section_2_last_description'),
        })
    )
   

admin.site.register(PrivacyPolicyCMSSupplier, PrivacyPolicyCMSSupplierAdmin)

class PrivacyPolicyCMSSupplier_SVAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - Privacy Policy', {
            'classes': ('collapse',),
            'fields': ('section_2_main_heading','section_2_left_heading','section_2_description','section_2_sub_heading','section_2_sub_description','section_2_last_heading','section_2_last_description'),
        })
    )
   

admin.site.register(PrivacyPolicyCMSSupplier_SV, PrivacyPolicyCMSSupplier_SVAdmin)
admin.site.register(NonBuiltInUserToken)


class TermsConditionCMSAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - Terms & Conditions', {
            'classes': ('collapse',),
            'fields': ('section_2_main_heading','section_2_left_heading','section_2_description'),
        })
    )
   

admin.site.register(TermsConditionCMS, TermsConditionCMSAdmin)

class TermsConditionCMS_SVAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - Terms & Conditions', {
            'classes': ('collapse',),
            'fields': ('section_2_main_heading','section_2_left_heading','section_2_description'),
        })
    )
   

admin.site.register(TermsConditionCMS_SV, TermsConditionCMS_SVAdmin)

class TermsConditionCMSSupplierAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - Terms & Conditions', {
            'classes': ('collapse',),
            'fields': ('section_2_main_heading','section_2_left_heading','section_2_description'),
        })
    )
   

admin.site.register(TermsConditionCMSSupplier, TermsConditionCMSSupplierAdmin)

class TermsConditionCMSSupplier_SVAdmin(admin.ModelAdmin):
    
       fieldsets = (
        ('Section 1 - Main', {
            'classes': ('collapse',),
            'fields': ('section_1_image','section_1_heading','section_1_button_text','section_1_button_link')
        }),
        ('Section 2 - Terms & Conditions', {
            'classes': ('collapse',),
            'fields': ('section_2_main_heading','section_2_left_heading','section_2_description'),
        })
    )
   

admin.site.register(TermsConditionCMSSupplier_SV, TermsConditionCMSSupplier_SVAdmin)

class UserSignupAdmin(admin.ModelAdmin):
    exclude = ('is_first_time_login','created_by','modified_by','is_authenticated','is_deleted','is_resetpassword','status','is_approved','is_login_from')
    list_display = ('email_id','user_type','status')
    search_fields = ['first_name','last_name','email_id']

    list_filter = ('user_type','status')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
         if db_field.name == "user_type":
                 kwargs["queryset"] = UserType.objects.all().exclude(user_type='User')
         return super(UserSignupAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

# class  authorAdmin(admin.ModelAdmin):
#     list_display=['image_tag','category_name']


# admin.site.register(CourseCategoryDetails,authorAdmin)


admin.site.register(UserSignup, UserSignupAdmin)
admin.site.site_header = 'Eddi Admin'
admin.site.register(EventAd)
admin.site.register(UserProfile)
admin.site.register(InvoiceData)
admin.site.register(InvoiceDataEvent)
admin.site.register(CourseRating)
admin.site.register(Notification)
admin.site.register(UserPaymentDetail)
admin.site.register(FavouriteCourse)
admin.site.register(CourseEnroll)
admin.site.register(RecruitmentAd)
admin.site.register(EventAdPaymentDetail)
admin.site.register(EventAdEnroll)
admin.site.register(MaterialVideoMaterial)
admin.site.register(MaterialDocumentMaterial)
admin.site.register(CourseMaterial)
admin.site.register(CourseMaterialStatus)
admin.site.register(WhatsonEddiCMS)
admin.site.register(PaybyInvoice)


admin.site.register(WhatsonEddiCMS_SV)
admin.site.register(ContactFormLead_SV)
admin.site.register(ContactFormLead)
admin.site.register(CourseBatch)
admin.site.register(BatchSession)
admin.site.register(SupplierAccountDetail)
admin.site.register(SupplierPayoutDetail)
admin.site.register(PlatformFeeCMS)
admin.site.register(SupplierWithdrawalDetail)
admin.site.register(EddiLabsCMS)
admin.site.register(EddiLabsCMS_SV)

