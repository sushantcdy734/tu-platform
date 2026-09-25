from django.contrib import admin
from .models import Event, EventRegistration


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    autocomplete_fields = ['user']
    readonly_fields = ['registered_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'college', 'start_datetime',
                    'venue', 'is_published', 'attendee_count']
    list_filter = ['event_type', 'is_published', 'college']
    search_fields = ['title', 'description', 'venue']
    date_hierarchy = 'start_datetime'
    autocomplete_fields = ['created_by']
    inlines = [EventRegistrationInline]

    fieldsets = (
        (None, {
            'fields': ('college', 'title', 'event_type', 'description',
                       'venue', 'organizer')
        }),
        ('Schedule', {
            'fields': ('start_datetime', 'end_datetime',
                       'registration_deadline')
        }),
        ('Meta', {
            'fields': ('is_published', 'created_by')
        }),
    )

    def attendee_count(self, obj):
        return obj.registrations.count()
    attendee_count.short_description = 'Attendees'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registered_at']
    list_filter = ['event__event_type']
    search_fields = ['user__username', 'event__title']
    autocomplete_fields = ['user', 'event']