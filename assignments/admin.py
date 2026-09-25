from django.contrib import admin
from .models import Assignment, Submission


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    autocomplete_fields = ['student']
    readonly_fields = ['submitted_at', 'updated_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'deadline', 'total_marks',
                    'created_by', 'submission_count', 'created_at']
    list_filter = ['subject__semester__program__department__college']
    search_fields = ['title', 'subject__name', 'subject__code']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['subject', 'created_by']
    inlines = [SubmissionInline]

    def submission_count(self, obj):
        return obj.submissions.count()
    submission_count.short_description = 'Submissions'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'status', 'marks_obtained', 'submitted_at']
    list_filter = ['status', 'assignment__subject']
    search_fields = ['student__username', 'assignment__title']
    autocomplete_fields = ['student', 'assignment']
    readonly_fields = ['submitted_at', 'updated_at']