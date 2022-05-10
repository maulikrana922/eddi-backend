from rest_framework import serializers

from .models import *

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSignup
        depth = 1

        fields = '__all__'

class CourseDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDetails
        depth = 2

        fields = '__all__'
class UerPaymentSerializer(serializers.ModelSerializer):
     class Meta:
        model = UserPaymentDetail
        depth = 1

        fields = '__all__'
        
class CourseEnrollSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseEnroll
        depth = 2

        # fields = ["supplier_email", "payment_detail", "user_profile"]
        fields = '__all__'






class SubCategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSubCategoryDetails
        depth = 1

        fields = '__all__'

class CategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategoryDetails
        depth = 1

        fields = '__all__'

class HomePageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomePageCMS
        depth = 1
        fields = '__all__'

class Header_FooterCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = Header_FooterCMS
        depth = 1
        fields = '__all__'

class PrivacyPolicyPageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivacyPolicyCMS
        depth = 1
        fields = '__all__'

class PrivacyPolicySupplierPageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivacyPolicyCMS
        depth = 1
        fields = '__all__'

class TermsConditionPageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = TermsConditionCMS
        depth = 1
        fields = '__all__'

class TermsConditionSupplierPageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = TermsConditionCMS
        depth = 1
        fields = '__all__'

class AboutUsCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = AboutUsPageCMS
        depth = 2
        fields = '__all__'

class ContactUsCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactUsPageCMS
        depth = 1
        fields = '__all__'


class BlogDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogDetails
        depth = 1

        fields = '__all__'



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        depth = 1

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
        depth = 1
        fields = '__all__'


class SupplierOrganizationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierOrganizationProfile
        depth = 1
        fields = '__all__'


class SupplierProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProfile
        depth = 1
        fields = '__all__'

class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        depth = 2
        fields = '__all__'


class CourseMaterialStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterialStatus
        depth = 2
        fields = '__all__'


class FavouriteCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteCourse
        depth = 1
        fields = '__all__'


class CourseDetailSerializer4courseenroll(serializers.ModelSerializer):
    supplier1 = serializers.SerializerMethodField('get_org')
    class Meta:
        model = CourseDetails
        depth = 2

        fields = ['uuid', 'supplier', 'course_image', 'course_name', 'course_level', 'course_length', 'course_category', 'course_subcategory', 'course_language', 'course_starting_date', 'course_for_organization', 'organization_domain', 'course_type', 'fee_type', 'course_price', 'var_charges', 'additional_information', 'organization_location', 'sub_area', 'course_checkout_link', 'meeting_link', 'meeting_passcode', 'created_by', 'is_approved', 'status', 'is_deleted', 'supplier1']

    def get_org(self, SupplierOrganizationProfile):
        supplier1 = SupplierOrganizationProfile.organizational_name
        return supplier1