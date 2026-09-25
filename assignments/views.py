from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission
from academics.models import Subject


@login_required
def teacher_assignments(request):
    """A teacher sees all assignments they've created."""
    if not request.user.is_teacher:
        messages.error(request, 'Only teachers can access this page.')
        return redirect('home')

    assignments = Assignment.objects.filter(
        created_by=request.user
    ).select_related('subject').order_by('-created_at')

    return render(request, 'assignments/teacher_list.html', {
        'assignments': assignments,
    })


@login_required
def assignment_detail(request, pk):
    """Teacher views submissions for one assignment."""
    if not request.user.is_teacher:
        messages.error(request, 'Only teachers can access this page.')
        return redirect('home')

    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    submissions = assignment.submissions.select_related('student').order_by('-submitted_at')

    if request.method == 'POST':
        # Grade a submission
        sub_id = request.POST.get('submission_id')
        marks = request.POST.get('marks_obtained', '').strip()
        feedback = request.POST.get('feedback', '').strip()

        submission = get_object_or_404(Submission, pk=sub_id, assignment=assignment)
        submission.marks_obtained = float(marks) if marks else None
        submission.feedback = feedback
        submission.status = 'graded' if marks else 'submitted'
        submission.save()

        messages.success(request, f'Graded {submission.student.get_full_name()}.')
        return redirect('assignment_detail', pk=pk)

    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment,
        'submissions': submissions,
    })


@login_required
def student_assignments(request):
    """A student sees all assignments for subjects they're enrolled in."""
    if not request.user.is_student:
        messages.error(request, 'Only students can view this page.')
        return redirect('home')

    # Find subjects the student has attendance or marks in
    # OR simpler: all subjects in their current semester
    try:
        profile = request.user.student_profile
        semester = profile.current_semester
    except Exception:
        semester = None

    if semester:
        assignments = Assignment.objects.filter(
            subject__semester=semester
        ).select_related('subject').order_by('-created_at')
    else:
        assignments = Assignment.objects.none()

    # Mark which ones have been submitted
    submitted_ids = set(
        Submission.objects.filter(student=request.user).values_list('assignment_id', flat=True)
    )

    return render(request, 'assignments/student_list.html', {
        'assignments': assignments,
        'submitted_ids': submitted_ids,
    })


@login_required
def submit_assignment(request, pk):
    """A student submits an assignment."""
    if not request.user.is_student:
        messages.error(request, 'Only students can submit.')
        return redirect('home')

    assignment = get_object_or_404(Assignment, pk=pk)

    if request.method == 'POST':
        # Check if already submitted
        existing = Submission.objects.filter(
            assignment=assignment, student=request.user
        ).first()

        if existing:
            messages.error(request, 'You already submitted this assignment.')
            return redirect('student_assignments')

        text = request.POST.get('text_answer', '').strip()
        file = request.FILES.get('file')

        if not text and not file:
            messages.error(request, 'Please provide an answer or upload a file.')
            return redirect('student_assignments')

        status = 'late' if assignment.is_past_deadline else 'submitted'

        Submission.objects.create(
            assignment=assignment,
            student=request.user,
            text_answer=text,
            file=file,
            status=status,
        )

        messages.success(request, 'Assignment submitted successfully.')
        return redirect('student_assignments')

    return render(request, 'assignments/submit.html', {
        'assignment': assignment,
    })