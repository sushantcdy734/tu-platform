from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'scope', 'college', 'department',
                    'posted_by', 'is_published', 'created_at']
    list_filter = ['scope', 'is_published', 'college']
    search_fields = ['title', 'body']
    date_hierarchy = 'created_at'
    list_editable = ['is_published']

    fieldsets = (
        (None, {
            'fields': ('title', 'body', 'scope', 'is_published')
        }),
        ('Targeting', {
            'fields': ('college', 'department'),
            'description': (
                'TU-wide notices ignore both fields. '
                'College notices require only College. '
                'Department notices require both College and Department.'
            ),
        }),
        ('Meta', {
            'fields': ('posted_by',),
        }),
    )