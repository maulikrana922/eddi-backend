from django.urls import path
from .views import *

urlpatterns = [
    # Stripe Link
    path('save-stripe-info/',Save_stripe_info.as_view(), name="stripe"),   
    path('user-payment-detail/',UserPaymentDetail_info.as_view(), name="UserPaymentDetail"),   
    path('free-courseEnroll/',Free_courseEnroll.as_view(), name="UserPaymentDetail"),   

    path('signup/',UserSignupView.as_view()),
    path('login/',UserLoginView.as_view()),
    path('forgot/',ForgetPasswordView.as_view()),
    path('changepassword/<str:uuid>/',ChangePasswordView.as_view(), name="changepassword"),
    path('resetpassword/',ResetPasswordView.as_view(), name="resetpassword"),
    path('get-user-details/<str:uuid>/',GetUserDetails.as_view()),
    path('get-user-details/',GetUserDetails.as_view()),

    path('add-course/',AddCourseView.as_view()), 
    path('get-course-details/<str:uuid>/',GetCourseDetails.as_view()),
    path('get-course-details/',GetCourseDetails.as_view()),
    path('favourite-course-details/',FavCourseDetails.as_view()),

    path('add-sub-category/',AddSubCategoryView.as_view()),
    path('get-sub-category-details/<str:uuid>/',GetSubCategoryDetails.as_view()),
    path('get-sub-category-details/',GetSubCategoryDetails.as_view()),

    path('get-category-details/',GetCategoryDetails.as_view()),
    path('get-category-details/<str:uuid>/',GetCategoryDetails.as_view()),

    path('get-blog-details/',GetBlogDetails.as_view()),
    path('get-blog-details/<str:uuid>/',GetBlogDetails.as_view()),
    
    
    path('view-individual-profile_User/',ViewIndividualProfile.as_view()),
    

    path('get-home-page-data/',GetHomePageDetails.as_view()),
    path('get-header-footer-data/',Header_FooterCMSDetails.as_view()),
    path('get-aboutus-page-data/',GetAboutUsPageDetails.as_view()),
    path('get-contactus-page-data/',GetContactUsPageDetails.as_view()),
    path('get-privacy-page-data/',GetPrivacyPolicyDetails.as_view()),
    path('get-terms-page-data/',GetTermsConditionDetails.as_view()),    
    path('contactus-form/',ContactFormView.as_view()),
    path('add-user-profile/',UserProfileView.as_view()),


# Supplier Dashboard

    path('supplier-dashboard/',SupplierDashboardView.as_view()),
    path('supplier-dashboard-Active_InActive/',SupplierDashboard_Active_InActiveView.as_view()),
    path('supplier-dashboard-courseGraph/',SupplierDashboard_courseGraphView.as_view()),
    path('supplier-dashboard-earningGraph/',SupplierDashboard_earningGraphView.as_view()),


# Event
    path('add-event/',EventView.as_view()),
    path('get-event/',EventView.as_view()),
    path('get-event/<str:uuid>/',EventView.as_view()),
    path('edit-event/<str:uuid>/',EventView.as_view()),
    path('delete-event/<str:uuid>/',EventView.as_view()),


# RecruitmentAd
    path('add-recruitment/',EventView.as_view()),
    path('get-recruitment/',EventView.as_view()),
    path('get-recruitment/<str:uuid>/',EventView.as_view()),
    path('edit-recruitment/<str:uuid>/',EventView.as_view()),
    path('delete-recruitment/<str:uuid>/',EventView.as_view()),

]