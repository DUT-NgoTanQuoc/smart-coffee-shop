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
        @role_required('manager', 'cashier')
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
            
            # Kiểm tra role của staff
            try:
                from apps.staff.models import Staff
                staff = Staff.objects.get(email=request.user.email, is_active=True)
                
                if staff.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'Bạn không có quyền truy cập chức năng này.')
                    return redirect('dashboard')
            except Staff.DoesNotExist:
                messages.error(request, 'Không tìm thấy thông tin nhân viên.')
                return redirect('dashboard')
        
        return wrapper
    return decorator


def manager_required(view_func):
    """
    Decorator yêu cầu role Manager
    Decorator requiring Manager role
    """
    return role_required('manager')(view_func)


def cashier_or_manager_required(view_func):
    """
    Decorator yêu cầu role Manager hoặc Cashier
    Decorator requiring Manager or Cashier role
    """
    return role_required('manager', 'cashier')(view_func)
