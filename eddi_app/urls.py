from django.urls import path
from .views import *

urlpatterns = [
    # Stripe Link
    path('save-stripe-info/',Save_stripe_info.as_view(), name="stripe"),   
    path('user-payment-detail/',UserPaymentDetail_info.as_view(), name="UserPaymentDetail"),   

    # Event Payment Flow
    path('save-stripe-infoevent/',Save_stripe_infoEvent.as_view(), name="eventstripe"),   
    path('event-payment-detail/',EventPaymentDetail_info.as_view(), name="EventPaymentDetail"),   

    # General Login/SignUp
    path('signup/',UserSignupView.as_view()),
    path('login/',UserLoginView.as_view()),
    path('forgot/',ForgetPasswordView.as_view()),
    path('changepassword/<str:uuid>/',ChangePasswordView.as_view(), name="changepassword"),
    path('verify-user/<str:uuid>/',VerifyUser.as_view(), name="VerifyUser"),
    path('resetpassword/',ResetPasswordView.as_view(), name="resetpassword"),

    # User Details
    path('get-user-details/<str:uuid>/',GetUserDetails.as_view()),
    path('get-user-details/',GetUserDetails.as_view()),

    # Course
    path('add-course/',AddCourseView.as_view()), 
    path('course-rating/<str:uuid>/',CourseRating.as_view(), name="CourseRating"),   
    path('get-course-details/<str:uuid>/',GetCourseDetails.as_view()),
    path('get-course-details/',GetCourseDetails.as_view()),
    path('favourite-course-details/',FavCourseDetails.as_view()),

    # Course Material
    path('course-material-upload/<str:uuid>/',CourseMaterialUpload.as_view()),
    path('course-material-status/',CourseMaterialStatus.as_view()),

    # Sub Category Details
    path('add-sub-category/',AddSubCategoryView.as_view()),
    path('get-sub-category-details/<str:uuid>/',GetSubCategoryDetails.as_view()),
    path('get-sub-category-details/',GetSubCategoryDetails.as_view()),

    # Category Details
    path('get-category-details/',GetCategoryDetails.as_view()),
    path('get-category-details/<str:uuid>/',GetCategoryDetails.as_view()),

    # Blog Details
    path('get-blog-details/',GetBlogDetails.as_view()),
    path('get-blog-details/<str:uuid>/',GetBlogDetails.as_view()),

    # Individual Profile
    path('view-individual-profile_User/',ViewIndividualProfile.as_view()),

    # CMS Pages
    path('whats-on-eddi/',Whats_On_Eddi.as_view()),
    path('get-home-page-data/',GetHomePageDetails.as_view()),
    path('testimonial/',Testimonial.as_view()),
    path('get-header-footer-data/',Header_FooterCMSDetails.as_view()),
    path('get-aboutus-page-data/',GetAboutUsPageDetails.as_view()),
    path('get-contactus-page-data/',GetContactUsPageDetails.as_view()),
    path('get-privacy-page-data/',GetPrivacyPolicyDetails.as_view()),
    path('get-terms-page-data/',GetTermsConditionDetails.as_view()),    
    path('get-privacySupplier-page-data/',GetPrivacyPolicySupplierDetails.as_view()),
    path('get-termsSupplier-page-data/',GetTermsConditionSupplierDetails.as_view()),    
    path('contactus-form/',ContactFormView.as_view()),
    path('add-user-profile/',UserProfileView.as_view()),

# Supplier Dashboard
    path('supplier-dashboard/',SupplierDashboardView.as_view()),
    path('supplier-dashboard-Active_InActive/',SupplierDashboard_Active_InActiveView.as_view()),
    path('supplier-dashboard-courseGraph/',SupplierDashboard_courseGraphView.as_view()),
    path('supplier-dashboard-earningGraph/',SupplierDashboard_earningGraphView.as_view()),

# Admin Dashboard
    path('admin-dashboard/',AdminDashboardView.as_view()),

# Events
    path('event/',EventView.as_view()),
    path('event/<str:uuid>/',EventView.as_view()),
    path('get-event-enroll/',EventEnrollView.as_view()),
    path('increase-Adcount/<str:uuid>/',IncreaseAdCount.as_view()),

# RecruitmentAds
    path('recruitmentAd/',RecruitmentAdView.as_view()),
    path('recruitmentAd/<str:uuid>/',RecruitmentAdView.as_view()),
    path('increase-recruitmentAdcount/<str:uuid>/',IncreaserecruitmentAdCount.as_view()),

    # My Space/My Course
    path('get-courseenrolldetail/',CourseEnrollView.as_view()),
    path('my-progressgraph/',MyProgressView.as_view()),

    # Supplier Organization Flow
    path('supplier-organization-profile/',SupplierOrganizationProfileview.as_view()),
    path('supplier-organization-profile-all/',SupplierOrganizationProfileviewall.as_view()),
    path('supplier-profile/',SupplierProfileView.as_view())

]