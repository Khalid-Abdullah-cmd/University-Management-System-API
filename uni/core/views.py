from rest_framework import generics
from .serializers import SignUpSerializer
from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated



class SignUpView(generics.CreateAPIView):
    
    permission_classes = [AllowAny]
    serializer_class = SignUpSerializer




class LoginView():


        pass   