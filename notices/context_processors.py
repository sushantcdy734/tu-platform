from .models import Notice


def notice_counts(request):
    """
    Makes `recent_notices`, `total_notices` and `recent_notice_count`
    available to every template automatically.
    """
    if not request.user.is_authenticated:
        return {}

    visible = Notice.visible_to(request.user)
    recent = visible[:5]

    # Count notices from the last 7 days — these are "new"
    from django.utils import timezone
    from datetime import timedelta
    one_week_ago = timezone.now() - timedelta(days=7)
    recent_count = visible.filter(created_at__gte=one_week_ago).count()

    return {
        'recent_notices': recent,
        'total_notices': visible.count(),
        'recent_notice_count': recent_count,
    }