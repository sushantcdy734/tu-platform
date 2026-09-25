from django.db import models
from django.conf import settings
from django.utils import timezone


class Event(models.Model):
    """
    A college event — seminar, workshop, sports, cultural, etc.
    """
    EVENT_TYPES = [
        ('seminar', 'Seminar'),
        ('workshop', 'Workshop'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural Program'),
        ('academic', 'Academic Event'),
        ('club', 'Club Activity'),
        ('competition', 'Competition'),
        ('function', 'College Function'),
        ('other', 'Other'),
    ]

    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='events',
    )
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    description = models.TextField()
    venue = models.CharField(max_length=200, blank=True)
    organizer = models.CharField(max_length=200, blank=True, help_text='Name of the organizing body or person')

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)

    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='events_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_datetime']

    def __str__(self):
        return f'{self.title} — {self.college.code}'

    @property
    def is_upcoming(self):
        return self.start_datetime >= timezone.now()

    @property
    def is_past(self):
        return self.start_datetime < timezone.now()

    @property
    def is_ongoing(self):
        if not self.end_datetime:
            return False
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime

    @property
    def days_until(self):
        delta = self.start_datetime - timezone.now()
        return delta.days

    @property
    def registration_open(self):
        if not self.registration_deadline:
            return self.is_upcoming
        return timezone.now() <= self.registration_deadline

    @property
    def attendee_count(self):
        return self.registrations.count()

    @property
    def event_type_color(self):
        return {
            'seminar': 'primary',
            'workshop': 'info',
            'sports': 'success',
            'cultural': 'warning',
            'academic': 'secondary',
            'club': 'dark',
            'competition': 'danger',
            'function': 'primary',
        }.get(self.event_type, 'secondary')


class EventRegistration(models.Model):
    """
    A user registering to attend an event.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_registrations',
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = [['event', 'user']]
        ordering = ['-registered_at']

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} → {self.event.title}'