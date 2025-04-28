from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Student, Instructor, Secretary, Appointment

admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(Secretary)
admin.site.register(Appointment)
