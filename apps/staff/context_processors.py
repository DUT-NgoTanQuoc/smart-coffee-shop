from django.contrib.auth import get_user_model
from .models import Staff


def staff_context(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}

    username = getattr(user, "username", None) or ""
    email = getattr(user, "email", None) or ""

    staff = None
    if username:
        staff = Staff.objects.filter(phone=username).first() or Staff.objects.filter(email=username).first()
    if not staff and email:
        staff = Staff.objects.filter(email=email).first()

    return {
        "current_staff": staff,
    }
