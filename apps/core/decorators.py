"""
Decorators cho role-based access control
Role-based access control decorators
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*allowed_roles):
    """
    Decorator kiểm tra quyền truy cập dựa trên role
    Decorator to check access permission based on role
    
    Usage:
        @role_required('admin', 'cashier')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Kiểm tra xem user đã đăng nhập chưa
            if not request.user.is_authenticated:
                messages.error(request, 'Vui lòng đăng nhập để tiếp tục.')
                return redirect('login')
            
            # Admin luôn có quyền truy cập
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Kiểm tra role của user (từ CustomAccountBackend)
            user_role = getattr(request.user, 'role', None)
            
            if user_role and user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Bạn không có quyền truy cập chức năng này.')
                return redirect('dashboard')
        
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator yêu cầu role Admin (superuser hoặc admin/manager role)
    Decorator requiring Admin role
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập.')
            return redirect('login')
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        user_role = getattr(request.user, 'role', None)
        if user_role in ['admin', 'manager']:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Chỉ Admin mới có quyền truy cập.')
        return redirect('dashboard')
    
    return wrapper


def cashier_required(view_func):
    """
    Decorator yêu cầu role Cashier trở lên (cashier hoặc admin)
    Decorator requiring Cashier role or higher
    """
    return role_required('admin', 'cashier')(view_func)


def barista_required(view_func):
    """
    Decorator yêu cầu role Barista trở lên (barista hoặc admin)
    Decorator requiring Barista role or higher
    """
    return role_required('admin', 'barista')(view_func)


def manager_required(view_func):
    """
    Decorator yêu cầu role Manager
    Decorator requiring Manager role
    """
    return role_required('manager', 'admin')(view_func)


def cashier_or_manager_required(view_func):
    """
    Decorator yêu cầu role Manager hoặc Cashier
    Decorator requiring Manager or Cashier role
    """
    return role_required('manager', 'cashier')(view_func)
