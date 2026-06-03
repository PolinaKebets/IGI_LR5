from django.utils import timezone


def time_context(request):
    """Add current time (UTC and Minsk) to all templates"""
    return {
        'now_utc': timezone.now(),
        'now_minsk': timezone.localtime(),
        'timezone': timezone.get_current_timezone_name(),
    }
