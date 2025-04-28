from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Student, Appointment, Instructor, Secretary

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404

from django import forms
from django.views.decorators.http import require_POST


from django.shortcuts import render, redirect, get_object_or_404

from .forms import StudentForm, SecretaryAppointmentForm, AppointmentForm, AppointmentFromDashboardForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password





# Gere la redircretion selon le role de l'utilisateur aprs login

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if hasattr(user, 'student'):
                return redirect('student_dashboard')
            elif hasattr(user, 'instructor'):
                return redirect('instructor_dashboard')
            elif hasattr(user, 'secretary'):
                return redirect('secretary_dashboard')
            elif user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('/') 

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})




# FICHE ELVE / STUDENT_DETAIL

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    user_role = None
    appointments = None


    if hasattr(request.user, 'student'):
        if request.user.student.id != student.id:
            return redirect('student_dashboard')
        user_role = 'student'


    elif hasattr(request.user, 'instructor'):
        if not Appointment.objects.filter(student=student, instructor=request.user.instructor).exists():
            return redirect('instructor_dashboard')
        user_role = 'instructor'
        appointments = Appointment.objects.filter(student=student, instructor=request.user.instructor)


    elif hasattr(request.user, 'secretary'):
        user_role = 'secretary'
        appointments = Appointment.objects.filter(student=student)

    elif request.user.is_superuser:
        user_role = 'admin'
        appointments = Appointment.objects.filter(student=student)

    else:
        return redirect('login')

    return render(request, 'student_detail.html', {'student': student, 'user_role': user_role, 'appointments': appointments})






# Dashboard student

@login_required
def student_dashboard(request):
    user = request.user

    try:
        student = Student.objects.get(user=user)
        appointments = Appointment.objects.filter(student=student).order_by('date', 'time')
    except Student.DoesNotExist:
        return render(request, 'student_dashboard.html', {
            'error': "Ce compte n'est pas lié à un profil étudiant."
        })

    return render(request, 'student_dashboard.html', {
        'student': student,
        'appointments': appointments
    })




# Dashboard instructeur

@login_required
def instructor_dashboard(request):
    user = request.user

    try:
        instructor = Instructor.objects.get(user=user)
        appointments = Appointment.objects.filter(instructor=instructor).order_by('date', 'time')
    except Instructor.DoesNotExist:
        return render(request, 'instructor_dashboard.html', {
            'error': "Ce compte n'est pas lié à un profil instructeur."
        })

    return render(request, 'instructor_dashboard.html', {
        'instructor': instructor,
        'appointments': appointments
    })







# formulaire de prise des rdv 

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }



# Ajout rdv

def create_appointment(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if student.hours_available <= 0:
        return render(request, 'create_appointment.html', {'error': "Cet élève n'a plus d'heures disponibles.", 'student': student})

    if hasattr(request.user, 'instructor'):
        form_class = AppointmentForm
    elif hasattr(request.user, 'secretary'):
        form_class = SecretaryAppointmentForm
    else:
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.student = student

            if hasattr(request.user, 'instructor'):
                appointment.instructor = Instructor.objects.get(user=request.user)

            appointment.save()
            student.hours_available -= 1
            student.save()

            if hasattr(request.user, 'secretary'):
                return redirect('manage_students')
            else:
                return redirect('instructor_dashboard')
    else:
        form = form_class()

    return render(request, 'create_appointment.html', {'form': form, 'student': student, 'user': request.user})



# delete rdv

@login_required
@require_POST
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if hasattr(request.user, 'instructor'):
        if appointment.instructor != request.user.instructor:
            return redirect('instructor_dashboard')

    elif not hasattr(request.user, 'secretary'):

        return redirect('student_dashboard')

    student = appointment.student
    appointment.delete()

    student.hours_available += 1
    student.save()

    if hasattr(request.user, 'secretary'):
        return redirect('manage_students')
    else:
        return redirect('instructor_dashboard')


# Edit rdv

@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)


    if hasattr(request.user, 'instructor'):
        instructor = Instructor.objects.get(user=request.user)
        if appointment.instructor != instructor:
            return redirect('instructor_dashboard')

    elif not (hasattr(request.user, 'secretary') or request.user.is_superuser):
        return redirect('login')


    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            updated = form.save(commit=False)

            conflict = Appointment.objects.filter(
                instructor=appointment.instructor,  
                date=updated.date,
                time=updated.time
            ).exclude(id=appointment.id).exists()

            if conflict:
                form.add_error(None, "Impossible : un autre rendez-vous existe déjà à ce créneau.")
            else:
                updated.save()

                if hasattr(request.user, 'instructor'):
                    return redirect('instructor_dashboard')
                else:
                    return redirect('global_planning')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'edit_appointment.html', {
        'form': form,
        'appointment': appointment
    })



# rdv depuis dashboard instructeur

class AppointmentFromDashboardForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=Student.objects.all())

    class Meta:
        model = Appointment
        fields = ['student', 'date', 'time', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }


@login_required
def create_appointment_from_dashboard(request):
    if hasattr(request.user, 'instructor'):
        instructor = Instructor.objects.get(user=request.user)
        students = Student.objects.all()
        form_class = AppointmentForm
    elif hasattr(request.user, 'secretary'):
        students = Student.objects.all()
        form_class = SecretaryAppointmentForm
    else:
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            student_id = request.POST.get('student')
            student = get_object_or_404(Student, id=student_id)
            appointment.student = student

            if hasattr(request.user, 'instructor'):
                appointment.instructor = instructor

            appointment.save()
            student.hours_available -= 1
            student.save()

            if hasattr(request.user, 'secretary'):
                return redirect('manage_students')
            else:
                return redirect('instructor_dashboard')
    else:
        form = form_class()

    return render(request, 'create_appointment.html', {'form': form, 'students': students, 'user': request.user})







# Secreataire dashboard

@login_required
def secretary_dashboard(request):
    user = request.user

    try:
        secretary = Secretary.objects.get(user=user)
    except Secretary.DoesNotExist:
        return render(request, 'secretary_dashboard.html', {
            'error': "Ce compte n'est pas lié à un profil secrétaire."
        })

    return render(request, 'secretary_dashboard.html', {
        'secretary': secretary
    })


# Planning pour Secretary

@login_required
def global_planning(request):
    appointments = Appointment.objects.all().order_by('date', 'time')
    return render(request, 'global_planning.html', {'appointments': appointments})



# Gerer les étudiants par le secretary

def manage_students(request):
    students = Student.objects.all()
    return render(request, 'manage_students.html', {'students': students})

def add_student(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        hours_available = request.POST.get('hours_available')

        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
        )

        Student.objects.create(
            user=user,
            hours_available=hours_available,
        )

        return redirect('manage_students')

    return render(request, 'add_student.html')

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('manage_students')
    else:
        form = StudentForm(instance=student)
    return render(request, 'edit_student.html', {'form': form, 'student': student})


def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == "POST":
        user = student.user  
        student.delete()     
        user.delete()        
        return redirect('manage_students')

    return redirect('manage_students')





# Gerer les instructeurs par le secretary

@login_required
def manage_instructors(request):
    instructors = Instructor.objects.all()
    return render(request, 'manage_instructors.html', {'instructors': instructors})

@login_required
def add_instructor(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
        )

        Instructor.objects.create(
            user=user,
        )

        return redirect('manage_instructors')

    return render(request, 'add_instructor.html')

@login_required
def edit_instructor(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    user = instructor.user

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password:  
            user.password = make_password(password)

        user.save()
        return redirect('manage_instructors')

    return render(request, 'edit_instructor.html', {'instructor': instructor})

@login_required
@require_POST
def delete_instructor(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    user = instructor.user

    appointments = Appointment.objects.filter(instructor=instructor)

    for appointment in appointments:
        student = appointment.student
        student.hours_available += 1
        student.save()
        appointment.delete()

    instructor.delete()
    user.delete()

    return redirect('manage_instructors')



# FICHE INSTRUCTEUR / INSTRUCTOR_DETAIL

@login_required
def instructor_detail(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    appointments = Appointment.objects.filter(instructor=instructor).order_by('date', 'time')
    return render(request, 'instructor_detail.html', {'instructor': instructor, 'appointments': appointments})


