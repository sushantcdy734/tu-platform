from django.contrib import admin
from .models import Lab, Equipment, LabBooking, MaintenanceRequest


class EquipmentInline(admin.TabularInline):
    model = Equipment
    extra = 0


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ['name', 'lab_type', 'college', 'location',
                    'capacity', 'in_charge', 'equipment_count', 'is_active']
    list_filter = ['lab_type', 'is_active', 'college']
    search_fields = ['name', 'location', 'description']
    autocomplete_fields = ['in_charge']
    inlines = [EquipmentInline]

    def equipment_count(self, obj):
        return obj.equipment.count()
    equipment_count.short_description = 'Equipment'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'lab', 'code', 'quantity', 'condition', 'purchased_date']
    list_filter = ['condition', 'lab']
    search_fields = ['name', 'code']
    autocomplete_fields = ['lab']


@admin.register(LabBooking)
class LabBookingAdmin(admin.ModelAdmin):
    list_display = ['lab', 'booked_by', 'date', 'start_time', 'end_time',
                    'status', 'expected_people', 'reviewed_by']
    list_filter = ['status', 'date', 'lab']
    search_fields = ['booked_by__username', 'purpose', 'lab__name']
    autocomplete_fields = ['lab', 'booked_by', 'reviewed_by']
    readonly_fields = ['created_at']


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'reported_by', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['issue', 'equipment__name']
    autocomplete_fields = ['equipment', 'reported_by', 'resolved_by']
    readonly_fields = ['created_at', 'updated_at']