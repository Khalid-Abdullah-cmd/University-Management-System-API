from rest_framework import generics
from .serializers import SignUpSerializer, CourseSerializer
from .models import Course, Enrollment, User
from rest_framework.permissions import AllowAny, IsAuthenticated


class CourseList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]

    queryset = Course.objects.all()
    serializer_class = CourseSerializer



class SignUpView(generics.CreateAPIView):
    
    permission_classes = [AllowAny]
    serializer_class = SignUpSerializer




class LoginView():


        pass   