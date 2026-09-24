from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, TeacherProfile


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    extra = 0
    fk_name = 'user'


class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    extra = 0
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name',
                    'role', 'college', 'is_active']
    list_filter = ['role', 'is_active', 'college']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('TU Platform', {'fields': ('role', 'phone', 'college', 'profile_picture')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('TU Platform', {'fields': ('role', 'phone', 'college')}),
    )

    def get_inlines(self, request, obj=None):
        """Show the correct profile inline based on the user's role."""
        if obj is None:
            return []
        if obj.role == 'student':
            return [StudentProfileInline]
        if obj.role == 'teacher':
            return [TeacherProfileInline]
        return []


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'roll_number', 'program', 'batch_year', 'current_semester']
    list_filter = ['program', 'batch_year', 'current_semester']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'roll_number']


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'designation', 'department', 'joining_date']
    list_filter = ['department', 'designation']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']