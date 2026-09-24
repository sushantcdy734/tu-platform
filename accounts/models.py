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