from django.urls import path
from . import views
from django.shortcuts import redirect
from django.urls import reverse

urlpatterns = [
    # dashboard / index page
    path("index/", views.student_dashboard, name="student_dashboard"),

    # redirect /attendance/ -> /attendance/index/
    path("", lambda request: redirect(reverse("student_dashboard"))),

    # other routes
    path("add_student/", views.add_student, name="add_student"),
    path("take_attendance/", views.take_attendance, name="take_attendance"),
    path("attendance_report/", views.attendance_report, name="attendance_report"),
    path("attendance_report/pdf/", views.generate_attendance_pdf, name="generate_attendance_pdf"),
]
