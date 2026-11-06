from django.urls import path
from.views import SignUpView, LoginView, CourseList, CourseDetails
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView


urlpatterns = [

    path("auth/signup/", SignUpView.as_view(),name="signup"),
    path("auth/login/", TokenObtainPairView.as_view()),    
    path("auth/refresh/", TokenRefreshView.as_view()),     
    path("auth/logout/", TokenBlacklistView.as_view()),
    
    path("course/", CourseList.as_view()),
    path("course/<int:id>", CourseDetails.as_view()),


]