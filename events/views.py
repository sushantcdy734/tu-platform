from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, EventRegistration


def _visible_events(user):
    if user.is_tu_admin:
        return Event.objects.filter(is_published=True)
    if user.college:
        return Event.objects.filter(college=user.college, is_published=True)
    return Event.objects.none()


@login_required
def event_list(request):
    qs = _visible_events(request.user)

    # Split into upcoming + past
    now = timezone.now()
    tab = request.GET.get('tab', 'upcoming')
    if tab == 'past':
        events = qs.filter(start_datetime__lt=now)
    else:
        events = qs.filter(start_datetime__gte=now)
        tab = 'upcoming'

    # Which events is the user registered for?
    registered_ids = set(
        EventRegistration.objects.filter(user=request.user).values_list('event_id', flat=True)
    )

    return render(request, 'events/list.html', {
        'events': events,
        'tab': tab,
        'registered_ids': registered_ids,
        'upcoming_count': qs.filter(start_datetime__gte=now).count(),
        'past_count': qs.filter(start_datetime__lt=now).count(),
    })


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)

    if not request.user.is_tu_admin and request.user.college != event.college:
        messages.error(request, 'Access denied.')
        return redirect('event_list')

    is_registered = EventRegistration.objects.filter(
        event=event, user=request.user
    ).exists()

    return render(request, 'events/detail.html', {
        'event': event,
        'is_registered': is_registered,
        'my_registration': EventRegistration.objects.filter(
            event=event, user=request.user
        ).first() if is_registered else None,
    })


@login_required
def event_register(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)

    if not request.user.is_tu_admin and request.user.college != event.college:
        messages.error(request, 'Access denied.')
        return redirect('event_list')

    if not event.registration_open:
        messages.error(request, 'Registration for this event is closed.')
        return redirect('event_detail', pk=pk)

    if request.method == 'POST':
        notes = request.POST.get('notes', '').strip()[:200]
        EventRegistration.objects.get_or_create(
            event=event,
            user=request.user,
            defaults={'notes': notes},
        )
        messages.success(request, f'You are now registered for {event.title}.')
        return redirect('event_detail', pk=pk)

    return render(request, 'events/register.html', {'event': event})


@login_required
def event_unregister(request, pk):
    event = get_object_or_404(Event, pk=pk)
    EventRegistration.objects.filter(event=event, user=request.user).delete()
    messages.success(request, 'You have unregistered from this event.')
    return redirect('event_detail', pk=pk)


@login_required
def event_attendees(request, pk):
    """Only admin/staff can see the list of attendees."""
    if not (request.user.is_tu_admin or request.user.is_college_admin or request.user.is_staff):
        messages.error(request, 'Only staff can view attendees.')
        return redirect('event_detail', pk=pk)

    event = get_object_or_404(Event, pk=pk)
    if not request.user.is_tu_admin and request.user.college != event.college:
        messages.error(request, 'Access denied.')
        return redirect('event_list')

    registrations = event.registrations.select_related('user').order_by('user__first_name')

    return render(request, 'events/attendees.html', {
        'event': event,
        'registrations': registrations,
    })