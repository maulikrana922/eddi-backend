from rest_framework import serializers

from .models import *

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSignup
        fields = '__all__'

class CourseDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDetails
        fields = '__all__'

class SubCategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSubCategoryDetails
        fields = '__all__'

class CategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategoryDetails
        fields = '__all__'

class HomePageCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomePageCMS
        depth = 1
        fields = '__all__'

class AboutUsCMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = AboutUsPageCMS
        depth = 1
        fields = '__all__'
