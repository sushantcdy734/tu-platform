from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from academics.models import Subject
from .models import AttendanceSession, AttendanceEntry
from accounts.models import User


@login_required
def student_attendance(request):
    """A student sees their own attendance per subject."""
    if not request.user.is_student:
        messages.error(request, 'Only students can view this page.')
        return redirect('home')

    # Every subject the student has entries in
    subjects = Subject.objects.filter(
        attendance_sessions__entries__student=request.user
    ).distinct()

    rows = []
    for s in subjects:
        total = AttendanceEntry.objects.filter(student=request.user, session__subject=s).count()
        present = AttendanceEntry.objects.filter(
            student=request.user, session__subject=s, status='present'
        ).count()
        pct = round((present / total) * 100, 1) if total else 0
        rows.append({
            'subject': s,
            'total': total,
            'present': present,
            'absent': total - present,
            'percent': pct,
        })

    return render(request, 'attendance/student_attendance.html', {'rows': rows})


@login_required
def teacher_attendance(request):
    """A teacher sees the sessions they've marked."""
    if not request.user.is_teacher:
        messages.error(request, 'Only teachers can view this page.')
        return redirect('home')

    sessions = AttendanceSession.objects.filter(
        marked_by=request.user
    ).select_related('subject')

    return render(request, 'attendance/teacher_attendance.html', {'sessions': sessions})