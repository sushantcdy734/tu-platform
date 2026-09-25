from django.db import models
from django.conf import settings


class Assignment(models.Model):
    """
    A teacher creates an assignment for a subject.
    """
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to='assignments/',
        blank=True,
        null=True,
        help_text='Optional: PDF, DOCX, ZIP, etc.',
    )
    deadline = models.DateTimeField(null=True, blank=True)
    total_marks = models.PositiveIntegerField(default=100)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assignments_created',
        limit_choices_to={'role': 'teacher'},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject.code} — {self.title}'

    @property
    def is_past_deadline(self):
        from django.utils import timezone
        if not self.deadline:
            return False
        return timezone.now() > self.deadline


class Submission(models.Model):
    """
    A student submits an assignment.
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('late', 'Late'),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        limit_choices_to={'role': 'student'},
    )
    file = models.FileField(
        upload_to='submissions/',
        blank=True,
        null=True,
    )
    text_answer = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')

    marks_obtained = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    feedback = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = [['assignment', 'student']]

    def __str__(self):
        return f'{self.student.get_full_name() or self.student.username} — {self.assignment.title}'