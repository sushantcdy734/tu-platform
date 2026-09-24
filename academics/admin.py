from django.contrib import admin
from .models import Department, Program, Semester, Subject


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'college', 'head']
    list_filter = ['college']
    search_fields = ['name', 'code']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'duration_years']
    list_filter = ['department__college']
    search_fields = ['name', 'code']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'program']
    list_filter = ['program__department__college']
    search_fields = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'semester', 'credits', 'teacher']
    list_filter = ['semester__program__department__college']
    search_fields = ['name', 'code']