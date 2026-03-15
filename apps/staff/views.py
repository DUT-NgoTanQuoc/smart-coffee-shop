from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Staff, WorkLog


@login_required
def staff_list(request):
    """Danh sách nhân viên"""
    staff_members = Staff.objects.all().order_by('name')
    
    # Lọc theo role
    role = request.GET.get('role')
    if role:
        staff_members = staff_members.filter(role=role)
    
    # Lọc active/inactive
    is_active = request.GET.get('is_active')
    if is_active:
        staff_members = staff_members.filter(is_active=is_active == 'true')
    
    context = {
        'staff_members': staff_members,
    }
    
    return render(request, 'staff/staff_list.html', context)


@login_required
def staff_detail(request, staff_id):
    """Chi tiết nhân viên"""
    staff = get_object_or_404(Staff, id=staff_id)
    work_logs = staff.work_logs.all().order_by('-work_date')[:30]
    
    context = {
        'staff': staff,
        'work_logs': work_logs,
    }
    
    return render(request, 'staff/staff_detail.html', context)


@login_required
def attendance_list(request):
    """Danh sách chấm công"""
    from django.utils import timezone
    
    # Lấy tháng hiện tại
    today = timezone.now().date()
    month = request.GET.get('month', today.month)
    year = request.GET.get('year', today.year)
    
    work_logs = WorkLog.objects.filter(
        work_date__month=month,
        work_date__year=year
    ).select_related('staff').order_by('-work_date')
    
    context = {
        'work_logs': work_logs,
        'month': month,
        'year': year,
    }
    
    return render(request, 'staff/attendance_list.html', context)
