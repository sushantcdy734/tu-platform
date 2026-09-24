from django.db import models
from django.conf import settings


class AttendanceSession(models.Model):
    """
    A single attendance-taking event.
    Example: 'Data Structures on 2026-09-25, Period 1' — marked by a teacher.
    """
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='attendance_sessions',
    )
    date = models.DateField()
    period = models.CharField(max_length=20, blank=True, help_text='e.g. 1st, 2nd, Lab')
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attendance_marked',
        limit_choices_to={'role': 'teacher'},
    )
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'subject']
        unique_together = [['subject', 'date', 'period']]

    def __str__(self):
        return f'{self.subject.code} — {self.date} {self.period}'.strip()

    @property
    def present_count(self):
        return self.entries.filter(status='present').count()

    @property
    def absent_count(self):
        return self.entries.filter(status='absent').count()

    @property
    def total_count(self):
        return self.entries.count()


class AttendanceEntry(models.Model):
    """
    One student's attendance status for one session.
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='entries',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_entries',
        limit_choices_to={'role': 'student'},
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')

    class Meta:
        unique_together = [['session', 'student']]
        ordering = ['student__first_name', 'student__last_name']

    def __str__(self):
        return f'{self.student.get_full_name() or self.student.username} — {self.get_status_display()}'