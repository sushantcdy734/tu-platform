from django.contrib import admin
from .models import Complaint, ComplaintUpdate


class ComplaintUpdateInline(admin.TabularInline):
    model = ComplaintUpdate
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'category', 'status', 'priority',
                    'college', 'submitted_by', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'category', 'college']
    search_fields = ['subject', 'description',
                     'submitted_by__username', 'submitted_by__first_name']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['submitted_by', 'assigned_to']
    inlines = [ComplaintUpdateInline]

    fieldsets = (
        (None, {
            'fields': ('college', 'submitted_by', 'category',
                       'subject', 'description')
        }),
        ('Status', {
            'fields': ('status', 'priority', 'assigned_to',
                       'resolution_note', 'resolved_at')
        }),
    )


@admin.register(ComplaintUpdate)
class ComplaintUpdateAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'author', 'old_status', 'new_status', 'created_at']
    list_filter = ['old_status', 'new_status']
    search_fields = ['message', 'complaint__subject']
    autocomplete_fields = ['complaint', 'author']