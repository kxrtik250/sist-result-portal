from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    register_number = models.CharField(max_length=20, unique=True)
    name            = models.CharField(max_length=100)
    department      = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.register_number} - {self.name}"


class Result(models.Model):
    student  = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    subject  = models.CharField(max_length=100)
    marks    = models.IntegerField()
    grade    = models.CharField(max_length=5)
    semester = models.CharField(max_length=20)

    class Meta:
        ordering = ['semester', 'subject']

    def __str__(self):
        return f"{self.student.register_number} - {self.subject}"


class AIAnalysis(models.Model):
    student          = models.OneToOneField(Student, on_delete=models.CASCADE)
    total_marks      = models.IntegerField(default=0)
    overall_grade    = models.CharField(max_length=5, default='N/A')
    performance      = models.CharField(max_length=50, default='')
    weak_subject     = models.CharField(max_length=100, default='')
    suggestion       = models.TextField(default='')
    cgpa             = models.CharField(max_length=10, default='0')
    subject_analysis = models.TextField(default='{}')
    strengths        = models.TextField(default='')
    predicted_cgpa   = models.CharField(max_length=10, default='0')
    generated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis - {self.student.name}"