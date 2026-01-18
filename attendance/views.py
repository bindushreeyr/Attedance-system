from django.shortcuts import render, redirect
from .models import Student,AttendanceMark
from django.contrib.auth.models import User,auth
from django.contrib.auth.models import User
from .forms import StudentForm,AttendanceMarkForm
from django.contrib.auth.models import Group,auth
from datetime import datetime
from django.db.models import Count, Q
from django.http import HttpResponse
from reportlab.pdfgen import canvas  # Import canvas for generating PDFs
from reportlab.lib.pagesizes import letter
from django.db.models import Count
from datetime import date



# Create your views here.
def index(request):
    return render(request,"index.html")

def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()  # Save only the student name
            return redirect('add_student')  # Redirect to the same page after adding
    else:
        form = StudentForm()

    students = Student.objects.all()  # Fetch all students

    return render(request, 'add_student.html', {'form': form, 'students': students})



from django.contrib import messages


from django.utils.timezone import now



def take_attendance(request):
    today = date.today()

    if request.method == 'POST':
        students = Student.objects.all()

        # Check if today's attendance already exists
        existing_attendance = AttendanceMark.objects.filter(date=today)

        if existing_attendance.exists():
            messages.error(request, "Attendance for today has already been submitted!")
            return redirect('take_attendance')

        # If not submitted yet, save attendance
        for student in students:
            status = request.POST.get(f'attendance_{student.sid}')
            if status:
                AttendanceMark.objects.create(student=student, status=status, date=today)

        messages.success(request, "Attendance submitted successfully for today!")
        return redirect('take_attendance')

    students = Student.objects.all()
    attendance_records = AttendanceMark.objects.filter(date=today)

    return render(request, 'take_attendance.html', {
        'students': students,
        'attendance_records': attendance_records,
        'today': today,
    })



def attendance_report(request):
    students = Student.objects.all()
    attendance_records = AttendanceMark.objects.select_related('student').all()
    
    # Get filter parameters from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    student_id = request.GET.get('student')

    if start_date and end_date:
        attendance_records = attendance_records.filter(date__range=[start_date, end_date])

    if student_id and student_id != "":
        attendance_records = attendance_records.filter(student__sid=student_id)
        students = students.filter(sid=student_id)  # Limit to one student

    # Calculate attendance percentage for selected students
    student_attendance = {}
    for student in students:
        total_classes = attendance_records.filter(student=student).count()
        present_count = attendance_records.filter(student=student, status="Present").count()

        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
        student_attendance[student] = attendance_percentage

    return render(request, 'attendance_report.html', {
        'students': students,
        'attendance_records': attendance_records,
        'student_attendance': student_attendance,
        'selected_start_date': start_date,
        'selected_end_date': end_date,
        'selected_student_id': student_id
    })

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from collections import defaultdict
from .models import AttendanceMark


def generate_attendance_pdf(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    student_id = request.GET.get("student")

    queryset = AttendanceMark.objects.all()

    # ---- Filters ----
    if start_date and start_date != "None":
        queryset = queryset.filter(date__gte=start_date)

    if end_date and end_date != "None":
        queryset = queryset.filter(date__lte=end_date)

    if student_id and student_id != "None":
        queryset = queryset.filter(student__id=student_id)

    # ---- Attendance Percentage Calculation ----
    attendance_summary = defaultdict(lambda: {"present": 0, "total": 0})

    for record in queryset:
        attendance_summary[record.student.student_name]["total"] += 1
        if record.status == "Present":
            attendance_summary[record.student.student_name]["present"] += 1

    # ---- Create PDF ----
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="attendance_report.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 14)

    y = 800
    p.drawString(50, y, "Attendance Report")
    y -= 30

    # =======================
    # TABLE 1: ATTENDANCE RECORDS
    # =======================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Attendance Records")
    y -= 20

    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Student Name")
    p.drawString(220, y, "Date")
    p.drawString(350, y, "Status")
    y -= 15

    p.setFont("Helvetica", 10)

    for record in queryset:
        p.drawString(50, y, record.student.student_name)
        p.drawString(220, y, record.date.strftime("%b %d, %Y"))
        p.drawString(350, y, record.status)
        y -= 15

        if y < 80:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = 800

    # =======================
    # TABLE 2: ATTENDANCE PERCENTAGE
    # =======================
    p.showPage()
    y = 800

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Attendance Percentage")
    y -= 20

    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Student Name")
    p.drawString(250, y, "Attendance %")
    y -= 15

    p.setFont("Helvetica", 10)

    for student, data in attendance_summary.items():
        if data["total"] > 0:
            percentage = (data["present"] / data["total"]) * 100
        else:
            percentage = 0

        p.drawString(50, y, student)
        p.drawString(250, y, f"{percentage:.2f}%")
        y -= 15

        if y < 80:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = 800

    p.save()
    return response





def student_dashboard(request):
    return render(request,"student_dashboard.html")


