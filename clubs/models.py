from django.db import models
from django.conf import settings


class Club(models.Model):
    """A student club within a college."""
    CATEGORY_CHOICES = [
        ('it', 'IT / Technology'),
        ('robotics', 'Robotics'),
        ('sports', 'Sports'),
        ('literary', 'Literary'),
        ('social', 'Social Service'),
        ('entrepreneurship', 'Entrepreneurship'),
        ('cultural', 'Cultural'),
        ('academic', 'Academic'),
        ('other', 'Other'),
    ]

    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='clubs',
    )
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='club_logos/', blank=True, null=True)

    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clubs_coordinated',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clubs_created',
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = [['college', 'name']]

    def __str__(self):
        return f'{self.name} — {self.college.code}'

    @property
    def member_count(self):
        return self.memberships.filter(status='approved').count()

    @property
    def pending_count(self):
        return self.memberships.filter(status='pending').count()

    @property
    def category_color(self):
        return {
            'it': 'primary', 'robotics': 'info', 'sports': 'success',
            'literary': 'warning', 'social': 'danger',
            'entrepreneurship': 'dark', 'cultural': 'primary',
            'academic': 'secondary',
        }.get(self.category, 'secondary')


class Membership(models.Model):
    """A student's membership in a club."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('left', 'Left'),
    ]
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('executive', 'Executive Member'),
        ('secretary', 'Secretary'),
        ('president', 'President'),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='club_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True, help_text='Why do you want to join this club?')

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='memberships_reviewed',
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [['club', 'user']]
        ordering = ['-requested_at']

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} → {self.club.name} ({self.get_status_display()})'

    @property
    def status_color(self):
        return {
            'pending': 'warning', 'approved': 'success',
            'rejected': 'danger', 'left': 'secondary',
        }.get(self.status, 'secondary')


class ClubAnnouncement(models.Model):
    """An announcement posted in a club."""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    body = models.TextField()
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='club_announcements_posted',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.club.name} — {self.title}'