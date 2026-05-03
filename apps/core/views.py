from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie


@method_decorator(never_cache, name='dispatch')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class SmartLoginView(LoginView):
    """Login view that always issues a fresh CSRF cookie."""

    template_name = 'registration/login.html'
    redirect_authenticated_user = True


def csrf_failure(request, reason=''):
    """
    Handle CSRF failures with a friendlier login recovery flow.
    """
    if request.path.startswith('/accounts/login'):
        messages.error(
            request,
            'Phiên đăng nhập đã hết hạn. Vui lòng tải lại trang và đăng nhập lại.',
        )
        return redirect('login')

    return HttpResponseForbidden(
        'CSRF verification failed. Reload the page and try again.'
    )
