from django.db import models

# Create your models here.

# Create your models here.
from django.contrib.auth.models import User

class Student(models.Model):
    sid = models.AutoField(primary_key=True)  # Student ID
    student_name = models.CharField(max_length=100)  # Student name

    def __str__(self):
        return self.student_name

class AttendanceMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date') 
    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"