"""Common public-template data."""

from .models import ClinicLocation, Doctor


def site_collections(request):
    if request.path.startswith("/admin/"):
        return {}
    return {
        "clinic_locations": ClinicLocation.objects.filter(
            is_active=True,
            live=True,
        ),
        "active_doctors": Doctor.objects.filter(is_active=True, live=True),
    }
