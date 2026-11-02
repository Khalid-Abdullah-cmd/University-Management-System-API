from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator



class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT="student", "Student"
        PROFESSOR = "professor", "Professor"
        ADMIN = "admin", 'Admin'

    role = models.CharField(max_length=30, choices=Role.choices, default=Role.STUDENT)


class Course(models.Model):

    title = models.CharField(max_length=50)
    course_code = models.CharField(max_length=70, unique=True)
    capacity = models.PositiveIntegerField()
    professor =  models.ForeignKey(User, limit_choices_to={'role': User.Role.PROFESSOR}, null= True, blank=True, on_delete=models.SET_NULL)
    
    
    def __str__(self):
        return self.title

    


class Enrollment(models.Model):


    student = models.ForeignKey(User, limit_choices_to={'role': User.Role.STUDENT}, on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE )
    grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course",
            ),
        ]

    def __str__(self):
            return f'{self.student.first_name} - {self.course.title} - {self.grade}'    


