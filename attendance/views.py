from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.core.mail import send_mail
import csv
from .models import Attendance
from django.shortcuts import render, redirect
from .models import Student
from .forms import StudentForm

# Create your views here.
def home(request):
    return render(request,"home.html")
from django.shortcuts import render, redirect



def attendance_list(request):
    return render(request, 'attendance_list.html') 



def attendance_list(request):
    attendance_records = Attendance.objects.all().order_by('-date')

    # Date filter logic
    search_date = request.GET.get('date')
    if search_date:
        attendance_records = attendance_records.filter(date=search_date)

    # Pagination logic (5 records per page)
    paginator = Paginator(attendance_records, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'attendance_list.html', {'attendance_list': page_obj})

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student', 'Date', 'Status'])

    for record in Attendance.objects.all():
        writer.writerow([record.student.name, record.date, record.status])

    return response

def mark_attendance(request, attendance_id):
    attendance = Attendance.objects.get(id=attendance_id)
    attendance.status = "Present" if attendance.status == "Absent" else "Absent"
    attendance.save()
    return JsonResponse({'status': attendance.status})

def send_report(request):
    subject = "Attendance Report"
    message = "Please find attached the latest attendance records."
    recipient_list = ["admin@example.com"]

    send_mail(subject, message, 'smartattendance@example.com', recipient_list)
    return JsonResponse({'message': 'Email Sent!'})




def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')  # Redirect to student list page
    else:
        form = StudentForm()
    return render(request, 'add_student.html', {'form': form})


def student_list(request):
    students = Student.objects.all()
    return render(request, 'attendance_list/student_list.html', {'students': students})

def students(request):
    return render(request, 'student_list.html')