# app/context_processors.py
from .models import SiteSettings

def site_settings(request):
    settings = SiteSettings.objects.first()  # Ensure there's only one instance
    return {
        'site_settings': settings,
    }
