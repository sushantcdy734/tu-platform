from django.db import models
from django.conf import settings


class Lab(models.Model):
    """A laboratory within a college."""
    LAB_TYPES = [
        ('computer', 'Computer Lab'),
        ('physics', 'Physics Lab'),
        ('chemistry', 'Chemistry Lab'),
        ('biology', 'Biology Lab'),
        ('electronics', 'Electronics Lab'),
        ('networking', 'Networking Lab'),
        ('other', 'Other'),
    ]

    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='labs',
    )
    name = models.CharField(max_length=150)
    lab_type = models.CharField(max_length=20, choices=LAB_TYPES, default='computer')
    location = models.CharField(max_length=200, blank=True, help_text='Building / room number')
    capacity = models.PositiveIntegerField(default=30, help_text='Max people')
    description = models.TextField(blank=True)

    in_charge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='labs_in_charge',
        limit_choices_to={'role__in': ['teacher', 'college_admin']},
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = [['college', 'name']]

    def __str__(self):
        return f'{self.name} — {self.college.code}'

    @property
    def equipment_count(self):
        return self.equipment.count()

    @property
    def working_count(self):
        return self.equipment.filter(condition='working').count()

    @property
    def type_color(self):
        return {
            'computer': 'primary',
            'physics': 'info',
            'chemistry': 'success',
            'biology': 'warning',
            'electronics': 'dark',
            'networking': 'secondary',
        }.get(self.lab_type, 'secondary')


class Equipment(models.Model):
    """A piece of equipment inside a lab."""
    CONDITION_CHOICES = [
        ('working', 'Working'),
        ('needs_repair', 'Needs Repair'),
        ('under_maintenance', 'Under Maintenance'),
        ('broken', 'Broken'),
    ]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True, help_text='Serial or asset tag')
    quantity = models.PositiveIntegerField(default=1)
    condition = models.CharField(max_length=25, choices=CONDITION_CHOICES, default='working')
    purchased_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.lab.name})'

    @property
    def condition_color(self):
        return {
            'working': 'success',
            'needs_repair': 'warning',
            'under_maintenance': 'info',
            'broken': 'danger',
        }.get(self.condition, 'secondary')


class LabBooking(models.Model):
    """A user's request to use a lab."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='bookings')
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lab_bookings',
    )
    purpose = models.TextField(help_text='What will you use the lab for?')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    expected_people = models.PositiveIntegerField(default=1)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='lab_bookings_reviewed',
    )
    reviewer_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f'{self.booked_by.username} → {self.lab.name} on {self.date}'

    @property
    def status_color(self):
        return {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'completed': 'secondary',
            'cancelled': 'dark',
        }.get(self.status, 'secondary')


class MaintenanceRequest(models.Model):
    """A request to repair / maintain equipment."""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_requests')
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='maintenance_reported',
    )
    issue = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='maintenance_resolved',
    )
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.equipment.name} — {self.get_status_display()}'

    @property
    def status_color(self):
        return {
            'open': 'warning',
            'in_progress': 'info',
            'resolved': 'success',
            'rejected': 'danger',
        }.get(self.status, 'secondary')

    @property
    def priority_color(self):
        return {
            'low': 'secondary',
            'normal': 'primary',
            'high': 'warning',
            'urgent': 'danger',
        }.get(self.priority, 'secondary')