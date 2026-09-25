from django.db import models
from django.conf import settings


class DocumentRequest(models.Model):
    """
    A request from a student for an official document.
    """
    DOCUMENT_TYPES = [
        ('bonafide', 'Bonafide Certificate'),
        ('character', 'Character Certificate'),
        ('recommendation', 'Recommendation Letter'),
        ('transcript', 'Transcript'),
        ('migration', 'Migration Certificate'),
        ('other', 'Other Document'),
    ]

    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
    ]

    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='document_requests',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_requests',
        limit_choices_to={'role': 'student'},
    )
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    purpose = models.TextField(help_text='Why do you need this document?')
    copies = models.PositiveIntegerField(default=1)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    admin_note = models.TextField(blank=True, help_text='Notes from college staff')
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents_handled',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.id} — {self.get_document_type_display()} ({self.student.username})'

    @property
    def status_color(self):
        return {
            'requested': 'secondary',
            'processing': 'info',
            'approved': 'primary',
            'ready': 'warning',
            'delivered': 'success',
            'rejected': 'danger',
        }.get(self.status, 'secondary')

    @property
    def is_open(self):
        return self.status in ('requested', 'processing', 'approved', 'ready')