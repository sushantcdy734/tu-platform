from django.db import models
from django.conf import settings


class Department(models.Model):
    """A department within a college."""
    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='departments',
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, help_text='Short code, e.g. CS')
    description = models.TextField(blank=True)
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
    """A degree program within a department."""
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='programs',
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    duration_years = models.PositiveIntegerField(default=4)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['department', 'name']
        unique_together = [['department', 'code']]

    def __str__(self):
        return f'{self.name} ({self.code})'


class Semester(models.Model):
    """A semester within a program."""
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='semesters',
    )
    number = models.PositiveIntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['program', 'number']
        unique_together = [['program', 'number']]

    def __str__(self):
        return f'{self.program.code} — {self.name}'


class Subject(models.Model):
    """A subject taught within a semester."""
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='subjects',
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    credits = models.PositiveIntegerField(default=3)
    description = models.TextField(blank=True)
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


class Exam(models.Model):
    """An exam for a specific subject."""
    EXAM_TYPES = [
        ('internal', 'Internal'),
        ('midterm', 'Mid-term'),
        ('final', 'Final'),
        ('practical', 'Practical'),
        ('project', 'Project'),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='exams',
    )
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES, default='internal')
    date = models.DateField(null=True, blank=True)
    total_marks = models.PositiveIntegerField(default=100)
    pass_marks = models.PositiveIntegerField(default=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'subject']
        unique_together = [['subject', 'name']]

    def __str__(self):
        return f'{self.subject.code} — {self.name}'


class Mark(models.Model):
    """A single student's marks for a single exam."""
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='marks',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='marks',
        limit_choices_to={'role': 'student'},
    )
    marks_obtained = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
    )
    is_absent = models.BooleanField(default=False)
    remarks = models.CharField(max_length=200, blank=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marks_entered',
        limit_choices_to={'role': 'teacher'},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-exam__date', 'student__first_name']
        unique_together = [['exam', 'student']]

    def __str__(self):
        return f'{self.student.get_full_name() or self.student.username} — {self.exam.name}'

    @property
    def percentage(self):
        if self.is_absent or self.marks_obtained is None:
            return None
        if not self.exam.total_marks:
            return None
        return round((float(self.marks_obtained) / self.exam.total_marks) * 100, 1)

    @property
    def passed(self):
        if self.is_absent or self.marks_obtained is None:
            return None
        return float(self.marks_obtained) >= self.exam.pass_marks

    @property
    def grade(self):
        pct = self.percentage
        if pct is None:
            return '—'
        if pct >= 90: return 'A+'
        if pct >= 80: return 'A'
        if pct >= 70: return 'B+'
        if pct >= 60: return 'B'
        if pct >= 50: return 'C+'
        if pct >= 40: return 'C'
        return 'F'