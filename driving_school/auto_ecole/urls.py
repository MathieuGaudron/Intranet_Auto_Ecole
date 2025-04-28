from django.urls import path
from .views import student_dashboard, instructor_dashboard, secretary_dashboard, student_detail, create_appointment, delete_appointment, edit_appointment, create_appointment_from_dashboard, global_planning, manage_students, add_student, edit_student, delete_student, manage_instructors, add_instructor, edit_instructor, delete_instructor, instructor_detail

urlpatterns = [
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('instructor/dashboard/', instructor_dashboard, name='instructor_dashboard'),
    path('secretary/dashboard/', secretary_dashboard, name='secretary_dashboard'),
    path('student/<int:student_id>/', student_detail, name='student_detail'),
    path('appointment/create/<int:student_id>/', create_appointment, name='create_appointment'),
    path('appointment/delete/<int:appointment_id>/', delete_appointment, name='delete_appointment'),
    path('appointment/edit/<int:appointment_id>/', edit_appointment, name='edit_appointment'),
    path('appointment/create/', create_appointment_from_dashboard, name='create_appointment_from_dashboard'),


    path('secretary/planning/', global_planning, name='global_planning'),
    path('secretary/manage_students/', manage_students, name='manage_students'),
    path('secretary/add_student/', add_student, name='add_student'),
    path('secretary/edit_student/<int:student_id>/', edit_student, name='edit_student'),
    path('secretary/delete_student/<int:student_id>/', delete_student, name='delete_student'),  

    path('secretary/manage_instructors/', manage_instructors, name='manage_instructors'),
    path('secretary/add_instructor/', add_instructor, name='add_instructor'),
    path('secretary/edit_instructor/<int:instructor_id>/', edit_instructor, name='edit_instructor'),
    path('secretary/delete_instructor/<int:instructor_id>/', delete_instructor, name='delete_instructor'),
    path('secretary/instructor/<int:instructor_id>/', instructor_detail, name='instructor_detail'),





]
