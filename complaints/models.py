from django.db import models
from django.conf import settings


class Complaint(models.Model):
    """
    A ticket submitted by a user (usually a student) to their college.
    College-scoped: only users of the same college can see it.
    """

    CATEGORY_CHOICES = [
        ('library', 'Library'),
        ('laboratory', 'Laboratory'),
        ('account', 'Account'),
        ('canteen', 'Canteen'),
        ('it', 'IT'),
        ('classroom', 'Classroom'),
        ('infrastructure', 'Infrastructure'),
        ('hostel', 'Hostel'),
        ('transportation', 'Transportation'),
        ('general', 'General'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Multi-tenant: every complaint belongs to a college
    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='complaints',
    )

    # Who submitted it
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='complaints_submitted',
    )

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    subject = models.CharField(max_length=200)
    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')

    # Who is handling it (assigned by admin/staff)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints_assigned',
    )

    resolution_note = models.TextField(
        blank=True,
        help_text='Filled when the complaint is resolved.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.id} — {self.subject} ({self.get_status_display()})'

    @property
    def is_open(self):
        return self.status in ('submitted', 'assigned', 'in_progress')

    @property
    def status_color(self):
        return {
            'submitted': 'secondary',
            'assigned': 'info',
            'in_progress': 'warning',
            'resolved': 'success',
            'closed': 'dark',
        }.get(self.status, 'secondary')

    @property
    def priority_color(self):
        return {
            'low': 'secondary',
            'normal': 'primary',
            'high': 'warning',
            'urgent': 'danger',
        }.get(self.priority, 'secondary')


class ComplaintUpdate(models.Model):
    """
    A comment / status change on a complaint.
    Optional but useful for tracking.
    """
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='updates',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='complaint_updates',
    )
    message = models.TextField()
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Update on #{self.complaint.id} by {self.author}'