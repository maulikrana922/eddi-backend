from rest_framework import serializers
from .models import *

class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UserTypeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = UserType
        depth = 1
        fields = '__all__'

class StatusSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = utl_status
        depth = 1
        fields = '__all__'

class ApprovalStatusSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = approval_status
        depth = 1
        fields = '__all__'

class UserSignupSerializer(DynamicFieldsModelSerializer):
    user_type = UserTypeSerializer(fields=('user_type',))
    status = StatusSerializer(fields=('value',))

    class Meta:
        model = UserSignup
        depth = 1
        fields = '__all__'

class CategoryDetailsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CourseCategoryDetails
        depth = 1
        fields = '__all__'

class SubCategoryDetailsSerializer(DynamicFieldsModelSerializer):
    supplier = UserSignupSerializer(fields=('first_name','email_id'))
    category_name = CategoryDetailsSerializer(fields=('category_name',))
    status = StatusSerializer(fields=('value',))
    is_approved = ApprovalStatusSerializer(fields=('value',))
    class Meta:
        model = CourseSubCategoryDetails
        depth = 1
        fields = '__all__'

class CourseDetailsSerializer(DynamicFieldsModelSerializer):
    supplier = UserSignupSerializer(fields=('first_name','last_name','email_id'))
    status = StatusSerializer(fields=('value',))
    is_approved = ApprovalStatusSerializer(fields=('value',))
    course_category = CategoryDetailsSerializer(fields=('category_name',))
    course_subcategory = SubCategoryDetailsSerializer(fields=('subcategory_name',))
    class Meta:
        model = CourseDetails
        depth = 2
        fields = '__all__'

class InvoiceDataSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = InvoiceData
        depth = 1
        fields = '__all__'

class UserPaymentSerializer(DynamicFieldsModelSerializer):
    course = CourseDetailsSerializer(fields=('course_name','supplier','course_image','course_category','course_subcategory','course_starting_date'))
    invoice = InvoiceDataSerializer(fields=('invoice_pdf',))
    is_approved = ApprovalStatusSerializer(fields=('value',))
    class Meta:
        model = UserPaymentDetail
        depth = 2
        fields = '__all__'
        
class CourseEnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnroll
        depth = 2
        fields = '__all__'




class WhatsOnEddiSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsonEddiCMS
        fields = '__all__'

class WhatsOnEddiSerializer_sv(serializers.ModelSerializer):
    class Meta:
        model = WhatsonEddiCMS_SV
        fields = '__all__'


class HomePageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomePageCMS
        depth = 2
        fields = '__all__'

class HomePageCMSSerializer_sv(serializers.ModelSerializer):

    class Meta:
        model = HomePageCMS_SV
        depth = 2
        fields = '__all__'

class TestinomialsDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestinomialsDetails
        depth = 1
        fields = '__all__'

class TestinomialsDetailsSerializer_sv(serializers.ModelSerializer):

    class Meta:
        model = TestinomialsDetails_SV
        depth = 1
        fields = '__all__'

class Header_FooterCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = Header_FooterCMS
        depth = 1
        fields = '__all__'

class Header_FooterCMSSerializer_sv(serializers.ModelSerializer):

    class Meta:
        model = Header_FooterCMS_SV
        depth = 1
        fields = '__all__'

class PrivacyPolicyPageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivacyPolicyCMS
        depth = 1
        fields = '__all__'

class PrivacyPolicyPageCMSSerializer_sv(serializers.ModelSerializer):

    class Meta:
        model = PrivacyPolicyCMS_SV
        depth = 1
        fields = '__all__'

class PrivacyPolicySupplierPageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivacyPolicyCMS
        depth = 1
        fields = '__all__'

class PrivacyPolicySupplierPageCMSSerializer_sv(serializers.ModelSerializer):

    class Meta:
        model = PrivacyPolicyCMS_SV
        depth = 1
        fields = '__all__'

class TermsConditionPageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = TermsConditionCMS
        depth = 1
        fields = '__all__'

class TermsConditionPageCMSSerializer_sv(serializers.ModelSerializer):

    class Meta:
        model = TermsConditionCMS_SV
        depth = 1
        fields = '__all__'

class TermsConditionSupplierPageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = TermsConditionCMS
        depth = 1
        fields = '__all__'

class TermsConditionSupplierPageCMSSerializer_sv(serializers.ModelSerializer):

    class Meta:
        model = TermsConditionCMS_SV
        depth = 1
        fields = '__all__'

class AboutUsCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = AboutUsPageCMS
        depth = 2
        fields = '__all__'

class AboutUsCMSSerializer_sv(serializers.ModelSerializer):

    class Meta:
        model = AboutUsPageCMS_SV
        depth = 2
        fields = '__all__'

class ContactUsCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactUsPageCMS
        depth = 1
        fields = '__all__'

class ContactUsCMSSerializer_sv(serializers.ModelSerializer):

    class Meta:
        model = ContactUsPageCMS_SV
        depth = 1
        fields = '__all__'


class BlogDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogDetails
        depth = 1

        fields = '__all__'

class BlogDetailsSerializer_sv(serializers.ModelSerializer):
    class Meta:
        model = BlogDetails_SV
        depth = 1

        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        depth = 2

        fields = '__all__'

class EventAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAd
        depth = 1

        fields = '__all__'

class EventAdEnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAdEnroll
        depth = 2

        fields = '__all__'

class EventAdPaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAdPaymentDetail
        depth = 2

        fields = '__all__'

class CourseRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRating
        depth = 2

        fields = '__all__'


class HeaderFooterCMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = Header_FooterCMS
        depth = 2
        fields = '__all__'

class RecruitmentAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitmentAd
        depth = 2
        fields = '__all__'


class SupplierOrganizationProfileSerializer(DynamicFieldsModelSerializer):
    usersignup = UserSignupSerializer(fields=('email_id',))
    status = StatusSerializer(fields=('value',))
    is_approved = ApprovalStatusSerializer(fields=('value',))

    class Meta:
        model = SupplierOrganizationProfile
        depth = 1
        fields = '__all__'

# class AdminProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdminProfile
#         depth = 1
#         fields = '__all__'


class SupplierProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProfile
        depth = 1
        fields = '__all__'


class CourseMaterialStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterialStatus
        depth = 2
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        depth = 1
        fields = '__all__'

class UserProfileCMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileCMS
        depth = 1
        fields = '__all__'


class UserProfileCMS_SVSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileCMS_SV
        depth = 1
        fields = '__all__'


class CourseMaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseMaterial
        depth = 2
        fields = '__all__'


class FavouriteCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteCourse
        depth = 1
        fields = '__all__'


# class testSerializer(SupplierProfileSerializer):
#     class Meta (SupplierProfileSerializer.Meta):
#         model = SupplierOrganizationProfile
#         depth = 1
#         fields = ('organizational_name', 'supplier_name')

class BatchDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseBatch
        depth = 2
        fields = '__all__'

class SessionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchSession
        depth = 2
        fields = '__all__'

class SupplierAccountDetailSerializer(DynamicFieldsModelSerializer):
    supplier = UserSignupSerializer(fields=('first_name','last_name','email_id'))
    class Meta:
        model = SupplierAccountDetail
        depth = 1
        fields = '__all__'

class SupplierWithdrawalSerializer(DynamicFieldsModelSerializer):
    supplier = SupplierAccountDetailSerializer(fields=('supplier','total_amount_due'))
    class Meta:
        model = SupplierWithdrawalDetail
        depth = 1
        fields = '__all__'