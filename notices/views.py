from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notice


@login_required
def notice_list(request):
    """Show all notices the logged-in user is allowed to see."""
    notices = Notice.visible_to(request.user)
    return render(request, 'notices/list.html', {
        'notices': notices,
    })