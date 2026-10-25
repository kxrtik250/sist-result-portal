
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Student, Result


class ResultPortalTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username="student_test",
            password="TestPassword123!",
        )
        self.student = Student.objects.create(
            user=self.student_user,
            register_number="TEST001",
            name="Test Student",
            department="Computer Science and Engineering",
        )

        self.other_user = User.objects.create_user(
            username="other_student",
            password="TestPassword123!",
        )
        self.other_student = Student.objects.create(
            user=self.other_user,
            register_number="TEST002",
            name="Other Student",
            department="Computer Science and Engineering",
        )

        self.staff_user = User.objects.create_user(
            username="staff_test",
            password="TestPassword123!",
            is_staff=True,
        )

    def test_student_login_redirects_to_student_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "student_test",
                "password": "TestPassword123!",
            },
        )

        self.assertRedirects(
            response,
            reverse("student_dashboard"),
        )

    def test_staff_login_redirects_to_staff_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "staff_test",
                "password": "TestPassword123!",
            },
        )

        self.assertRedirects(
            response,
            reverse("staff_dashboard"),
        )

    def test_student_only_sees_their_own_results(self):
        own_result = Result.objects.create(
            student=self.student,
            subject="Programming in Python",
            marks=85,
            grade="A",
            semester="Semester 2",
        )
        Result.objects.create(
            student=self.other_student,
            subject="Database Management Systems",
            marks=92,
            grade="O",
            semester="Semester 4",
        )

        self.client.force_login(self.student_user)
        response = self.client.get(reverse("student_dashboard"))

        self.assertEqual(response.status_code, 200)

        visible_results = list(response.context["results"])
        self.assertEqual(visible_results, [own_result])
        self.assertNotIn(
            "Database Management Systems",
            [result.subject for result in visible_results],
        )

    def test_staff_cannot_add_marks_above_100(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("add_result"),
            {
                "register_number": "TEST001",
                "subject": "Programming in Python",
                "marks": "101",
                "grade": "O",
                "semester": "Semester 2",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Marks must be between 0 and 100.")
        self.assertFalse(
            Result.objects.filter(student=self.student).exists()
        )

