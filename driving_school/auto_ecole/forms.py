from django import forms
from .models import Appointment, Instructor, Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['hours_available']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

class SecretaryAppointmentForm(forms.ModelForm):
    instructor = forms.ModelChoiceField(queryset=Instructor.objects.all(), required=True)

    class Meta:
        model = Appointment
        fields = ['instructor', 'date', 'time', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

class AppointmentFromDashboardForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), required=True)

    class Meta:
        model = Appointment
        fields = ['student', 'date', 'time', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }


class InstructorForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Instructor
        fields = []
