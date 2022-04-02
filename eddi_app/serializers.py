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
    # my_field = serializers.SerializerMethodField('is_named_bar')

    # def is_named_bar(self, foo):
    #     return foo.name == "bar"

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

class PrivacyPolicyPageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivacyPolicyCMS
        depth = 1
        fields = '__all__'

class TermsConditionPageCMSSerializer(serializers.ModelSerializer):

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