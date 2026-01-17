from django import forms
from .models import Student
from .models import AttendanceMark

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [ 'student_name'] 


class AttendanceMarkForm(forms.ModelForm):
    class Meta:
        model = AttendanceMark
        fields = ['student', 'status']  # Date is auto-filled