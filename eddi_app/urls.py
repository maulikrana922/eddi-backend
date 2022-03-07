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


]