from django.db import models
from django.conf import settings


class Department(models.Model):
    """
    A department within a college.
    Example: "Department of Computer Science" within KCT.
    """
    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='departments',
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, help_text='Short code, e.g. CS')
    description = models.TextField(blank=True)

    # Department head — a teacher
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['college', 'name']
        unique_together = [['college', 'code']]

    def __str__(self):
        return f'{self.name} — {self.college.code}'


class Program(models.Model):
    """
    A degree program within a department.
    Example: "BSc CSIT", "BCA", "BBA".
    """
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='programs',
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, help_text='Short code, e.g. BSCSIT')
    duration_years = models.PositiveIntegerField(default=4)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['department', 'name']
        unique_together = [['department', 'code']]

    def __str__(self):
        return f'{self.name} ({self.code})'


class Semester(models.Model):
    """
    A semester within a program (1, 2, 3, ..., 8).
    """
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='semesters',
    )
    number = models.PositiveIntegerField(help_text='1, 2, 3, … 8')
    name = models.CharField(max_length=50, help_text='e.g. "First Semester"')

    class Meta:
        ordering = ['program', 'number']
        unique_together = [['program', 'number']]

    def __str__(self):
        return f'{self.program.code} — {self.name}'


class Subject(models.Model):
    """
    A subject taught within a semester.
    Example: "Data Structures" in BSc CSIT Semester 3.
    """
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='subjects',
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, help_text='Short code, e.g. CSC201')
    credits = models.PositiveIntegerField(default=3)
    description = models.TextField(blank=True)

    # Optional: teacher assigned to teach this subject
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_subjects',
        limit_choices_to={'role': 'teacher'},
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['semester', 'name']
        unique_together = [['semester', 'code']]

    def __str__(self):
        return f'{self.code} — {self.name}'