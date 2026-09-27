from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Lab, Equipment, LabBooking, MaintenanceRequest


def _visible_labs(user):
    if user.is_tu_admin:
        return Lab.objects.filter(is_active=True)
    if user.college:
        return Lab.objects.filter(college=user.college, is_active=True)
    return Lab.objects.none()


def _is_staff_user(user):
    return user.is_tu_admin or user.is_college_admin or user.is_staff


@login_required
def lab_list(request):
    labs = _visible_labs(request.user)
    return render(request, 'laboratory/list.html', {'labs': labs})


@login_required
def lab_detail(request, pk):
    lab = get_object_or_404(Lab, pk=pk, is_active=True)

    if not request.user.is_tu_admin and request.user.college != lab.college:
        messages.error(request, 'Access denied.')
        return redirect('lab_list')

    equipment = lab.equipment.all()
    my_bookings = LabBooking.objects.filter(
        lab=lab, booked_by=request.user
    ).order_by('-date')

    is_lab_staff = _is_staff_user(request.user) or lab.in_charge == request.user

    # Pending bookings for staff to review
    pending = lab.bookings.filter(status='pending') if is_lab_staff else []

    return render(request, 'laboratory/detail.html', {
        'lab': lab,
        'equipment': equipment,
        'my_bookings': my_bookings,
        'pending': pending,
        'is_lab_staff': is_lab_staff,
    })


@login_required
def lab_book(request, pk):
    lab = get_object_or_404(Lab, pk=pk, is_active=True)

    if not request.user.is_tu_admin and request.user.college != lab.college:
        messages.error(request, 'Access denied.')
        return redirect('lab_list')

    if request.method == 'POST':
        purpose = request.POST.get('purpose', '').strip()
        date = request.POST.get('date')
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')
        try:
            people = max(1, int(request.POST.get('expected_people', 1)))
        except (TypeError, ValueError):
            people = 1

        if not purpose or not date or not start or not end:
            messages.error(request, 'All fields are required.')
        elif start >= end:
            messages.error(request, 'End time must be after start time.')
        else:
            LabBooking.objects.create(
                lab=lab,
                booked_by=request.user,
                purpose=purpose,
                date=date,
                start_time=start,
                end_time=end,
                expected_people=people,
                status='pending',
            )
            messages.success(request, 'Booking request submitted.')
            return redirect('lab_detail', pk=pk)

    return render(request, 'laboratory/book.html', {'lab': lab})


@login_required
def booking_review(request, pk, booking_id):
    lab = get_object_or_404(Lab, pk=pk)
    booking = get_object_or_404(LabBooking, pk=booking_id, lab=lab)

    is_lab_staff = _is_staff_user(request.user) or lab.in_charge == request.user
    if not is_lab_staff:
        messages.error(request, 'Only lab in-charge can review bookings.')
        return redirect('lab_detail', pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action', '')
        note = request.POST.get('reviewer_note', '').strip()
        if action in ('approve', 'reject'):
            booking.status = 'approved' if action == 'approve' else 'rejected'
            booking.reviewed_by = request.user
            booking.reviewed_at = timezone.now()
            booking.reviewer_note = note
            booking.save()
            messages.success(request, f'Booking {booking.status}.')
        return redirect('lab_detail', pk=pk)

    return redirect('lab_detail', pk=pk)


@login_required
def my_bookings(request):
    qs = LabBooking.objects.filter(booked_by=request.user).select_related('lab').order_by('-date')
    return render(request, 'laboratory/my_bookings.html', {'bookings': qs})


@login_required
def report_maintenance(request, equipment_id):
    equipment = get_object_or_404(Equipment, pk=equipment_id)

    if not request.user.is_tu_admin and request.user.college != equipment.lab.college:
        messages.error(request, 'Access denied.')
        return redirect('lab_list')

    if request.method == 'POST':
        issue = request.POST.get('issue', '').strip()
        priority = request.POST.get('priority', 'normal')
        if not issue:
            messages.error(request, 'Describe the issue.')
        else:
            MaintenanceRequest.objects.create(
                equipment=equipment,
                reported_by=request.user,
                issue=issue,
                priority=priority,
                status='open',
            )
            messages.success(request, 'Maintenance request submitted.')
            return redirect('lab_detail', pk=equipment.lab.id)

    return render(request, 'laboratory/report_maintenance.html', {'equipment': equipment})


@login_required
def maintenance_list(request):
    if not _is_staff_user(request.user):
        messages.error(request, 'Only staff can view all maintenance requests.')
        return redirect('lab_list')

    qs = MaintenanceRequest.objects.select_related('equipment', 'equipment__lab', 'reported_by')
    if not request.user.is_tu_admin:
        qs = qs.filter(equipment__lab__college=request.user.college)

    return render(request, 'laboratory/maintenance_list.html', {'requests': qs})