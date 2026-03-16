"""Context processors for core app"""
from apps.core.models import Account


def user_account(request):
    """Add user account to context if authenticated"""
    context = {}
    if request.user.is_authenticated:
        try:
            # Try to get Account from custom table
            account = Account.objects.get(username=request.user.username)
            context['user_account'] = account
        except Account.DoesNotExist:
            context['user_account'] = None
    return context
