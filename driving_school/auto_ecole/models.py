from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import User

# Étudiant
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hours_available = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} (Student)"

# Instructeur
class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} (Instructor)"

# Secrétaire
class Secretary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} (Secretary)"

# Rendez-vous
class Appointment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.date} - {self.time} - {self.student.user.username} avec {self.instructor.user.username}"
