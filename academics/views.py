from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Exam, Mark


@login_required
def teacher_exams(request):
    """A teacher sees all exams for subjects they teach."""
    if not request.user.is_teacher:
        messages.error(request, 'Only teachers can access this page.')
        return redirect('home')

    exams = Exam.objects.filter(
        subject__teacher=request.user
    ).select_related('subject').annotate(
        student_count=Count('marks')
    ).order_by('-date')

    return render(request, 'academics/teacher_exams.html', {
        'exams': exams,
    })


@login_required
def exam_marks(request, exam_id):
    """A teacher views/edits marks for a single exam."""
    if not request.user.is_teacher:
        messages.error(request, 'Only teachers can access this page.')
        return redirect('home')

    exam = get_object_or_404(Exam, pk=exam_id, subject__teacher=request.user)

    if request.method == 'POST':
        for mark in exam.marks.all():
            marks_key = f'marks_{mark.id}'
            absent_key = f'absent_{mark.id}'
            remarks_key = f'remarks_{mark.id}'

            mark.is_absent = absent_key in request.POST
            if mark.is_absent:
                mark.marks_obtained = None
            else:
                val = request.POST.get(marks_key, '').strip()
                mark.marks_obtained = float(val) if val else None
            mark.remarks = request.POST.get(remarks_key, '').strip()
            mark.entered_by = request.user
            mark.save()

        messages.success(request, f'Saved marks for {exam.name}.')
        return redirect('exam_marks', exam_id=exam.id)

    return render(request, 'academics/exam_marks.html', {
        'exam': exam,
        'marks': exam.marks.select_related('student').order_by(
            'student__first_name', 'student__last_name'
        ),
    })


@login_required
def student_results(request):
    """A student sees all their marks."""
    if not request.user.is_student:
        messages.error(request, 'Only students can view this page.')
        return redirect('home')

    marks = Mark.objects.filter(
        student=request.user
    ).select_related('exam', 'exam__subject').order_by('-exam__date')

    total_exams = marks.count()
    passed = sum(1 for m in marks if m.passed is True)
    failed = sum(1 for m in marks if m.passed is False)

    subjects = {}
    for m in marks:
        s = m.exam.subject
        if s not in subjects:
            subjects[s] = []
        subjects[s].append(m)

    return render(request, 'academics/student_results.html', {
        'marks': marks,
        'subjects': subjects,
        'total_exams': total_exams,
        'passed': passed,
        'failed': failed,
    })