from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Club, Membership, ClubAnnouncement


def _visible_clubs(user):
    if user.is_tu_admin:
        return Club.objects.filter(is_active=True)
    if user.college:
        return Club.objects.filter(college=user.college, is_active=True)
    return Club.objects.none()


@login_required
def club_list(request):
    clubs = _visible_clubs(request.user)
    memberships = Membership.objects.filter(user=request.user)
    approved_ids = set(memberships.filter(status='approved').values_list('club_id', flat=True))
    pending_ids = set(memberships.filter(status='pending').values_list('club_id', flat=True))

    return render(request, 'clubs/list.html', {
        'clubs': clubs,
        'approved_ids': approved_ids,
        'pending_ids': pending_ids,
    })


@login_required
def club_detail(request, pk):
    club = get_object_or_404(Club, pk=pk, is_active=True)

    if not request.user.is_tu_admin and request.user.college != club.college:
        messages.error(request, 'Access denied.')
        return redirect('club_list')

    my_membership = Membership.objects.filter(club=club, user=request.user).first()

    is_club_admin = (
        request.user.is_tu_admin
        or request.user.is_college_admin
        or request.user.is_staff
        or club.coordinator == request.user
    )

    members = club.memberships.filter(status='approved').select_related('user')
    pending = club.memberships.filter(status='pending').select_related('user') if is_club_admin else []
    announcements = club.announcements.select_related('posted_by')

    return render(request, 'clubs/detail.html', {
        'club': club,
        'my_membership': my_membership,
        'is_club_admin': is_club_admin,
        'members': members,
        'pending': pending,
        'announcements': announcements,
    })


@login_required
def club_join(request, pk):
    club = get_object_or_404(Club, pk=pk, is_active=True)

    if not request.user.is_tu_admin and request.user.college != club.college:
        messages.error(request, 'Access denied.')
        return redirect('club_list')

    existing = Membership.objects.filter(club=club, user=request.user).first()
    if existing and existing.status in ('approved', 'pending'):
        messages.info(request, 'You already have a membership or a pending request.')
        return redirect('club_detail', pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if existing and existing.status in ('rejected', 'left'):
            existing.status = 'pending'
            existing.reason = reason
            existing.save()
        else:
            Membership.objects.create(club=club, user=request.user, reason=reason, status='pending')
        messages.success(request, f'Your request to join {club.name} has been submitted.')
        return redirect('club_detail', pk=pk)

    return render(request, 'clubs/join.html', {'club': club})


@login_required
def club_leave(request, pk):
    club = get_object_or_404(Club, pk=pk)
    Membership.objects.filter(club=club, user=request.user).update(status='left')
    messages.success(request, f'You have left {club.name}.')
    return redirect('club_detail', pk=pk)


@login_required
def membership_review(request, pk, membership_id):
    club = get_object_or_404(Club, pk=pk)
    membership = get_object_or_404(Membership, pk=membership_id, club=club)

    is_club_admin = (
        request.user.is_tu_admin or request.user.is_college_admin
        or request.user.is_staff or club.coordinator == request.user
    )
    if not is_club_admin:
        messages.error(request, 'Only club coordinators can review memberships.')
        return redirect('club_detail', pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'approve':
            membership.status = 'approved'
            membership.reviewed_by = request.user
            membership.reviewed_at = timezone.now()
            membership.save()
            messages.success(request, f'Approved {membership.user.get_full_name() or membership.user.username}.')
        elif action == 'reject':
            membership.status = 'rejected'
            membership.reviewed_by = request.user
            membership.reviewed_at = timezone.now()
            membership.save()
            messages.success(request, f'Rejected {membership.user.get_full_name() or membership.user.username}.')
        return redirect('club_detail', pk=pk)

    return redirect('club_detail', pk=pk)


@login_required
def club_announce(request, pk):
    club = get_object_or_404(Club, pk=pk)
    is_club_admin = (
        request.user.is_tu_admin or request.user.is_college_admin
        or request.user.is_staff or club.coordinator == request.user
    )
    if not is_club_admin:
        messages.error(request, 'Only club coordinators can post announcements.')
        return redirect('club_detail', pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        if not title or not body:
            messages.error(request, 'Title and body are required.')
        else:
            ClubAnnouncement.objects.create(club=club, title=title, body=body, posted_by=request.user)
            messages.success(request, 'Announcement posted.')
        return redirect('club_detail', pk=pk)

    return render(request, 'clubs/announce.html', {'club': club})