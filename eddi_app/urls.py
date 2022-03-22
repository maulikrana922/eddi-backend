from django.urls import path
from .views import *

urlpatterns = [
    path('signup/',UserSignupView.as_view()),
    path('login/',UserLoginView.as_view()),
    path('changepassword/<str:uuid>/',ChangePasswordView.as_view()),
    path('get-user-details/<str:uuid>/',GetUserDetails.as_view()),
    path('get-user-details/',GetUserDetails.as_view()),

    path('add-course/',AddCourseView.as_view()), 
    path('get-course-details/<str:uuid>/',GetCourseDetails.as_view()),
    path('get-course-details/',GetCourseDetails.as_view()),

    path('add-sub-category/',AddSubCategoryView.as_view()),
    path('get-sub-category-details/<str:uuid>/',GetSubCategoryDetails.as_view()),
    path('get-sub-category-details/',GetSubCategoryDetails.as_view()),

    path('get-category-details/',GetCategoryDetails.as_view()),
    path('get-category-details/<str:uuid>/',GetCategoryDetails.as_view()),

    path('get-blog-details/',GetBlogDetails.as_view()),
    path('get-blog-details/<str:uuid>/',GetBlogDetails.as_view()),

    path('get-home-page-data/',GetHomePageDetails.as_view()),
    path('get-aboutus-page-data/',GetAboutUsPageDetails.as_view()),
    path('get-contactus-page-data/',GetContactUsPageDetails.as_view()),
    path('get-privacy-page-data/',GetPrivacyPolicyDetails.as_view()),
    path('get-terms-page-data/',GetTermsConditionDetails.as_view()),



    
    path('contactus-form/',ContactFormView.as_view())


]