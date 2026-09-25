from django.contrib import admin
from .models import Department, Program, Semester, Subject, Exam, Mark


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


class MarkInline(admin.TabularInline):
    model = Mark
    extra = 0
    autocomplete_fields = ['student']
    fields = ['student', 'marks_obtained', 'is_absent', 'remarks']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'exam_type', 'date',
                    'total_marks', 'pass_marks']
    list_filter = ['exam_type', 'date', 'subject__semester__program__department__college']
    search_fields = ['name', 'subject__name', 'subject__code']
    date_hierarchy = 'date'
    inlines = [MarkInline]


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'marks_obtained', 'is_absent', 'entered_by']
    list_filter = ['is_absent', 'exam__subject']
    search_fields = ['student__username', 'exam__name']
    autocomplete_fields = ['student', 'exam', 'entered_by']