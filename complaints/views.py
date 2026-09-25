from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Complaint, ComplaintUpdate


def _visible_complaints(user):
    """Return the complaints this user is allowed to see (multi-tenant rule)."""
    if user.is_tu_admin:
        return Complaint.objects.all()
    if user.college:
        return Complaint.objects.filter(college=user.college)
    return Complaint.objects.none()


@login_required
def complaint_list(request):
    """List of complaints the user can see.
    Students see only their own; staff/admins see their college's."""
    qs = _visible_complaints(request.user)

    if request.user.is_student:
        qs = qs.filter(submitted_by=request.user)

    # Optional filters
    status = request.GET.get('status', '').strip()
    category = request.GET.get('category', '').strip()
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category=category)

    return render(request, 'complaints/list.html', {
        'complaints': qs,
        'status_choices': Complaint.STATUS_CHOICES,
        'category_choices': Complaint.CATEGORY_CHOICES,
        'current_status': status,
        'current_category': category,
    })


@login_required
def complaint_create(request):
    """Submit a new complaint. Only students and teachers."""
    if request.user.is_tu_admin or request.user.is_college_admin:
        messages.error(request, 'Admins cannot submit complaints from here.')
        return redirect('complaint_list')

    if not request.user.college:
        messages.error(request, 'You need to be part of a college to submit a complaint.')
        return redirect('complaint_list')

    if request.method == 'POST':
        category = request.POST.get('category', 'general')
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'normal')

        if not subject or not description:
            messages.error(request, 'Subject and description are required.')
            return render(request, 'complaints/create.html', {
                'category_choices': Complaint.CATEGORY_CHOICES,
                'priority_choices': Complaint.PRIORITY_CHOICES,
                'form_data': request.POST,
            })

        complaint = Complaint.objects.create(
            college=request.user.college,
            submitted_by=request.user,
            category=category,
            subject=subject,
            description=description,
            priority=priority,
        )

        messages.success(request, f'Complaint #{complaint.id} submitted successfully.')
        return redirect('complaint_detail', pk=complaint.id)

    return render(request, 'complaints/create.html', {
        'category_choices': Complaint.CATEGORY_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
    })


@login_required
def complaint_detail(request, pk):
    """View a single complaint with its updates."""
    complaint = get_object_or_404(Complaint, pk=pk)

    # Access check: only staff of same college or the submitter
    if not request.user.is_tu_admin:
        if request.user.college != complaint.college:
            messages.error(request, 'You do not have access to this complaint.')
            return redirect('complaint_list')
        if request.user.is_student and complaint.submitted_by != request.user:
            messages.error(request, 'You can only view your own complaints.')
            return redirect('complaint_list')

    if request.method == 'POST':
        # Only staff / admins can update status and add notes
        if request.user.is_student:
            messages.error(request, 'Only staff can update complaints.')
            return redirect('complaint_detail', pk=pk)

        new_status = request.POST.get('status', '').strip()
        message = request.POST.get('message', '').strip()

        old_status = complaint.status

        if new_status and new_status in dict(Complaint.STATUS_CHOICES):
            complaint.status = new_status
            if new_status == 'resolved' and not complaint.resolved_at:
                complaint.resolved_at = timezone.now()

        if message:
            ComplaintUpdate.objects.create(
                complaint=complaint,
                author=request.user,
                message=message,
                old_status=old_status,
                new_status=new_status or old_status,
            )

        complaint.save()
        messages.success(request, f'Complaint #{complaint.id} updated.')
        return redirect('complaint_detail', pk=pk)

    return render(request, 'complaints/detail.html', {
        'complaint': complaint,
        'status_choices': Complaint.STATUS_CHOICES,
        'updates': complaint.updates.select_related('author'),
    })


@login_required
def complaint_assign(request, pk):
    """Admin assigns the complaint to themselves or another staff member."""
    if not (request.user.is_tu_admin or request.user.is_college_admin or request.user.is_staff):
        messages.error(request, 'Only admins can assign complaints.')
        return redirect('complaint_detail', pk=pk)

    complaint = get_object_or_404(Complaint, pk=pk)

    if not request.user.is_tu_admin and complaint.college != request.user.college:
        messages.error(request, 'You cannot assign this complaint.')
        return redirect('complaint_detail', pk=pk)

    complaint.assigned_to = request.user
    if complaint.status == 'submitted':
        complaint.status = 'assigned'
    complaint.save()

    ComplaintUpdate.objects.create(
        complaint=complaint,
        author=request.user,
        message=f'Complaint assigned to {request.user.get_full_name() or request.user.username}.',
        old_status='submitted',
        new_status=complaint.status,
    )

    messages.success(request, 'Complaint assigned to you.')
    return redirect('complaint_detail', pk=pk)