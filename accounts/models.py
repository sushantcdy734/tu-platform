from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for the TU Platform.

    Roles:
        TU_ADMIN      - University-wide administrator
        COLLEGE_ADMIN - Administrator for a single college
        TEACHER       - Teacher / instructor
        STUDENT       - Student
    """

    ROLE_CHOICES = [
        ('tu_admin', 'TU Administrator'),
        ('college_admin', 'College Administrator'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Which college does this user belong to?
    # NULL for TU admins only.
    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    # ---------- Convenience helpers ----------
    @property
    def is_tu_admin(self):
        return self.role == 'tu_admin' or self.is_superuser

    @property
    def is_college_admin(self):
        return self.role == 'college_admin'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'


class StudentProfile(models.Model):
    """
    Extra student-specific information.
    One-to-one with User (role='student').
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'student'},
    )
    program = models.ForeignKey(
        'academics.Program',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
    )
    roll_number = models.CharField(max_length=30, blank=True)
    batch_year = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='e.g. 2024'
    )
    admission_date = models.DateField(null=True, blank=True)
    current_semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_students',
    )

    def __str__(self):
        return f'Student: {self.user.get_full_name() or self.user.username}'


class TeacherProfile(models.Model):
    """
    Extra teacher-specific information.
    One-to-one with User (role='teacher').
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        limit_choices_to={'role': 'teacher'},
    )
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers',
    )
    designation = models.CharField(
        max_length=100,
        blank=True,
        help_text='e.g. Lecturer, Assistant Professor',
    )
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Teacher: {self.user.get_full_name() or self.user.username}'