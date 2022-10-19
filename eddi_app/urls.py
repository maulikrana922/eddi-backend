from django.urls import path
from .views import *
from .webhook import stripe_webhook

urlpatterns = [
    # Stripe Link
    path('save-stripe-info/',Save_stripe_info.as_view(), name="stripe"),   
    path('user-payment-detail/',UserPaymentDetail_info.as_view(), name="UserPaymentDetail"),   
    path('paybyinvoice/',PayByInvoice.as_view(), name="PayByInvoice"),   

    # Event Payment Flow
    path('save-stripe-infoevent/',Save_stripe_infoEvent.as_view(), name="eventstripe"),   
    path('event-payment-detail/',EventPaymentDetail_info.as_view(), name="EventPaymentDetail"),   


    path('manage-payment/',Manage_Payment.as_view(), name="ManagePayment"),   
    path('admin-manage-payment/',Admin_Manage_Payment.as_view(), name="AdminManagePayment"),   
    path('manage-payment/<str:uuid>/',Manage_Payment.as_view(), name="ManagePayment"),   
    path('admin-payment-list/',GetAdminPaymentList.as_view(), name="GetAdminPaymentList"),
    path('admin-payment-list/<str:uuid>/',GetAdminPaymentList.as_view(), name="GetAdminPaymentList"),

    path('save-stripe-account/',SaveStripeAccount.as_view(),name="SaveStripeAccount"),
    path('get-account-detail/',GetAccountDetail.as_view(),name="GetAccountDetail"),
    path('supplier-withdraw-request/',SupplierWithDrawRequest.as_view(),name="SupplierWithDrawRequest"),
    path('supplier-withdraw-list/',SupplierWithDrawDetails.as_view(),name="SupplierWithDrawDetails"),
    path('supplier-withdraw-status/<str:uuid>/',SupplierWithDrawStatus.as_view(),name="SupplierWithDrawStatus"),
    
    path('supplier-payout/<str:uuid>/',SupplierPayout.as_view(),name="SupplierPayout"),
    path('stripe-webhook/',stripe_webhook,name="StripeWebhook"),

    # General Login/SignUp
    path('signup/',UserSignupView.as_view()),
    path('login/',UserLoginView.as_view()),
    path('forgot/',ForgetPasswordView.as_view()),
    path('changepassword/<str:uuid>/',ChangePasswordView.as_view(), name="changepassword"),
    path('verify-user/<str:uuid>/',VerifyUser.as_view(), name="VerifyUser"),
    path('resetpassword/<str:uuid>/',ResetPasswordView.as_view(), name="resetpassword"),
    path('resetpassword/',ResetPasswordView.as_view(), name="resetpassword"),

    # User Details
    path('get-user-details/<str:uuid>/',GetUserDetails.as_view()),
    path('get-user-details/',GetUserDetails.as_view()),

    # Course
    path('add-course/',AddCourseView.as_view()), 
    path('course-rating/<str:uuid>/',CourseRating.as_view(), name="CourseRating"),   
    path('course-rating-admin/',CourseRatingAdmin.as_view(), name="CourseRatingAdmin"),   
    path('course-rating-admin/<str:uuid>/',CourseRatingAdmin.as_view(), name="CourseRatingAdmin"),   
    path('get-course-details/<str:uuid>/',GetCourseDetails.as_view()),
    path('get-course-details/',GetCourseDetails.as_view()),
    path('favourite-course-details/',FavCourseDetails.as_view()),

    # Course Material
    path('course-material-upload/<str:uuid>/',CourseMaterialUpload.as_view()),
    path('course-material-status/',CourseMaterialStatus.as_view()),

    # Sub Category Details
    path('all-sub-category/',AllSubCategory.as_view()),
    path('add-sub-category/',AddSubCategoryView.as_view()),
    path('get-sub-category-details/<str:uuid>/',GetSubCategoryDetails.as_view()),
    path('get-sub-category-details/',GetSubCategoryDetails.as_view()),
    path('get-sub-category-list/<str:uuid>/',GetSubCategoryList.as_view()),

    # Category Details
    path('get-category-details/',GetCategoryDetails.as_view()),
    path('get-category-details/<str:uuid>/',GetCategoryDetails.as_view()),

    # Blog Details
    path('get-blog-details/',GetBlogDetails.as_view()),
    path('get-blog-details/<str:uuid>/',GetBlogDetails.as_view()),
    path('sw/get-blog-details/',GetBlogDetails_sv.as_view()),
    path('sw/get-blog-details/<str:uuid>/',GetBlogDetails_sv.as_view()),

    # Individual Profile
    path('view-individual-profile_User/',ViewIndividualProfile.as_view()),
    path('add-user-profile/',UserProfileView.as_view()),
    # path('admin-profile/',AdminProfileView.as_view()),


    # CMS Pages
    path('userprofile-cms/',User_Profile_CMS.as_view()),
    path('sw/userprofile-cms/',User_Profile_CMS_sv.as_view()),
    path('whats-on-eddi/',Whats_On_Eddi.as_view()),
    path('sw/whats-on-eddi/',Whats_On_Eddi_sv.as_view()),
    path('get-home-page-data/',GetHomePageDetails.as_view()),
    path('sw/get-home-page-data/',GetHomePageDetails_sv.as_view()),
    path('testimonial/',Testimonial.as_view()),
    path('sw/testimonial/',Testimonial_sv.as_view()),
    path('get-header-footer-data/',Header_FooterCMSDetails.as_view()),
    path('sw/get-header-footer-data/',Header_FooterCMSDetails_sv.as_view()),
    path('get-aboutus-page-data/',GetAboutUsPageDetails.as_view()),
    path('sw/get-aboutus-page-data/',GetAboutUsPageDetails_sv.as_view()),
    path('get-contactus-page-data/',GetContactUsPageDetails.as_view()),
    path('sw/get-contactus-page-data/',GetContactUsPageDetails_sv.as_view()),
    path('get-privacy-page-data/',GetPrivacyPolicyDetails.as_view()),
    path('sw/get-privacy-page-data/',GetPrivacyPolicyDetails_sv.as_view()),
    path('get-privacySupplier-page-data/',GetPrivacyPolicySupplierDetails.as_view()),
    path('sw/get-privacySupplier-page-data/',GetPrivacyPolicySupplierDetails_sv.as_view()),
    path('get-terms-page-data/',GetTermsConditionDetails.as_view()),    
    path('sw/get-terms-page-data/',GetTermsConditionDetails_sv.as_view()),    
    path('get-termsSupplier-page-data/',GetTermsConditionSupplierDetails.as_view()),    
    path('sw/get-termsSupplier-page-data/',GetTermsConditionSupplierDetails_sv.as_view()),    
    path('contactus-form/',ContactFormView.as_view()),
    path('sw/contactus-form/',ContactFormView_sv.as_view()),
    path('get-eddilabs-page-data/',EddiLabsDetailCms.as_view()),
    path('sw/get-eddilabs-page-data/',EddiLabsDetailCms_sv.as_view()),
    
# Supplier Dashboard
    path('supplier-dashboard/',SupplierDashboardView.as_view()),
    path('supplier-dashboard-Active_InActive/',SupplierDashboard_Active_InActiveView.as_view()),
    path('supplier-dashboard-courseGraph/',SupplierDashboard_courseGraphView.as_view()),
    path('supplier-dashboard-earningGraph/',SupplierDashboard_earningGraphView.as_view()),

# Admin Dashboard
    path('admin-dashboard/',AdminDashboardView.as_view()),
    path('admin-dashboard-users/',AdminDashboardUserView.as_view()),
    path('admin-dashboard-suppliers/',AdminDashboardSupplierView.as_view()),

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
    path('supplier-organization-profile-adminview/',SupplierOrganizationProfileAdminview.as_view()),
    # path('supplier-organization-profile-all/',SupplierOrganizationProfileviewall.as_view()),
    path('supplier-profile/',SupplierProfileView.as_view()),
    
    # Notification
    path('notifications/',Notification.as_view()),
    
    # Batch And Session
    path('get-allcourse-list/',GetCourseListView.as_view()),
    path('add-batch/',AddBatchView.as_view()),
    path('get-batch/',GetBatchView.as_view()),
    path('get-batch/<str:uuid>/',GetBatchView.as_view()),
    path('add-session/',AddSessionView.as_view()),
    path('get-session/',GetSessionView.as_view()),
    path('get-session/<str:uuid>/',GetSessionView.as_view()),
    path('get-user-session/',GetUserSessionView.as_view()),

]
