from django.contrib import admin
from .models import DocumentRequest


@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'document_type', 'status',
                    'copies', 'college', 'created_at']
    list_filter = ['status', 'document_type', 'college']
    search_fields = ['student__username', 'student__first_name', 'purpose']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['student', 'handled_by']

    fieldsets = (
        (None, {
            'fields': ('college', 'student', 'document_type',
                       'purpose', 'copies')
        }),
        ('Processing', {
            'fields': ('status', 'handled_by', 'admin_note',
                       'ready_at', 'delivered_at')
        }),
    )