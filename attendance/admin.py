from django.contrib import admin
from .models import AttendanceSession, AttendanceEntry


class AttendanceEntryInline(admin.TabularInline):
    model = AttendanceEntry
    extra = 0
    autocomplete_fields = ['student']


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'date', 'period', 'marked_by',
                    'present_count', 'absent_count', 'total_count']
    list_filter = ['date', 'subject__semester__program__department__college']
    search_fields = ['subject__name', 'subject__code']
    inlines = [AttendanceEntryInline]


@admin.register(AttendanceEntry)
class AttendanceEntryAdmin(admin.ModelAdmin):
    list_display = ['session', 'student', 'status']
    list_filter = ['status']
    search_fields = ['student__username', 'student__first_name', 'student__last_name']