from django.shortcuts import render
from colleges.models import College, District


def home(request):
    """Public landing page + logged-in dashboard."""
    context = {
        'districts': District.objects.all(),
        'colleges': College.objects.filter(status='active')[:6],
        'total_colleges': College.objects.filter(status='active').count(),
        'total_districts': District.objects.count(),
    }
    return render(request, 'home.html', context)