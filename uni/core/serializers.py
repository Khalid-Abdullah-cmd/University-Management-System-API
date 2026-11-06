from rest_framework import serializers
from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator 
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Course, Enrollment, User




class SignUpSerializer(serializers.ModelSerializer):

    password_confirm = serializers.CharField(max_length=128, write_only=True, style={"input_type":"password"})
    password = serializers.CharField(max_length=128,write_only=True,style={"input_type":"password"} )


    role = serializers.ChoiceField(choices=[User.Role.STUDENT, User.Role.PROFESSOR], default=User.Role.STUDENT)


    #to accept usernames with spaces and no numbers 
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z]+( [A-Za-z]+)*$",
                message="Username can only contain letters and single spaces.",
            ),
            UniqueValidator(queryset=User.objects.all(), lookup="iexact"),
        ],
    )

    class Meta:
        model = User
        fields = ['username', 'role', 'password', 'password_confirm']



    def validate_role(self,value):

        if value not in ['student', 'professor']:
            raise serializers.ValidationError({'role': 'role must be either student or professor and in lower case'})
        return value


    def validate(self, data):


        if data['password_confirm'] != data['password']:
            raise serializers.ValidationError({"password": "passwords did not match"})
        try:
                
                validate_password(data["password"], user=User(username=data["username"]))
        except DjangoValidationError as e:
                raise serializers.ValidationError({"password": list(e.messages)})

        
        return data
        
    
    def create(self, data):

        data.pop("password_confirm")
        return User.objects.create_user(**data)        



class CourseSerializer(serializers.ModelSerializer):


    title = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z]+( [A-Za-z]+)*$",
                message="Course title can only contain letters and single spaces.",
            ),
            UniqueValidator(queryset=User.objects.all(), lookup="iexact"),
        ],
    )

    class Meta:

        model = Course
        fields = ['title', 'course_code', 'capacity', 'professor']


    def validate_capacity(self, data):

        if data['capacity'] < 0:
              
              raise serializers.ValidationError("Course capacity should be a Positive Integer or a 0")
             
          