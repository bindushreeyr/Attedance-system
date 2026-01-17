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

def generate_attendance_pdf(request):
    students = Student.objects.all()
    attendance_records = AttendanceMark.objects.all()

    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    student_id = request.GET.get('student')

    if start_date and end_date:
        attendance_records = attendance_records.filter(date__range=[start_date, end_date])

    if student_id and student_id != "":
        attendance_records = attendance_records.filter(student__sid=student_id)
        students = students.filter(sid=student_id)  # Limit to one student

    # Calculate attendance percentage
    student_attendance = {}
    for student in students:
        total_classes = attendance_records.filter(student=student).count()
        present_count = attendance_records.filter(student=student, status="Present").count()
        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
        student_attendance[student] = attendance_percentage

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, height - 40, "Attendance Report")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 80, "Student ID")
    p.drawString(120, height - 80, "Name")
    p.drawString(250, height - 80, "Date")
    p.drawString(350, height - 80, "Status")
    p.drawString(450, height - 80, "Attendance %")

    y = height - 100
    p.setFont("Helvetica", 10)

    for record in attendance_records.order_by('student__sid', 'date'):
        student = record.student
        percentage = student_attendance.get(student, 0)
        
        p.drawString(50, y, str(student.sid))
        p.drawString(120, y, student.student_name)
        p.drawString(250, y, record.date.strftime("%Y-%m-%d"))
        p.drawString(350, y, record.status)
        p.drawString(450, y, f"{percentage:.2f}%")
        y -= 20

        if y < 50:  # If page is full, add a new page
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - 50

    p.save()
    return response




def student_dashboard(request):
    return render(request,"student_dashboard.html")


