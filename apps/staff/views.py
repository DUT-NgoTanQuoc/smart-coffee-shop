from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

from .models import Staff, WorkLog
from .forms import StaffForm


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
def staff_create(request):
    """Tạo nhân viên và tài khoản đăng nhập"""
    initial_username = None
    form = StaffForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            staff = form.save()
            form.sync_user(staff)
            messages.success(request, 'Đã tạo nhân viên và tài khoản đăng nhập.')
            return redirect('staff_list')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin.')

    return render(request, 'staff/staff_form.html', {'form': form, 'mode': 'create'})


@login_required
def staff_update(request, staff_id):
    """Cập nhật nhân viên và tài khoản đăng nhập"""
    staff = get_object_or_404(Staff, id=staff_id)

    # Lấy username từ bảng accounts (nếu staff_id khớp)
    initial_username = ''
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT username FROM accounts WHERE staff_id = %s", [staff_id])
        result = cursor.fetchone()
        if result:
            initial_username = result[0]
    
    # Nếu không tìm được, thử lấy từ Django User
    if not initial_username:
        User = get_user_model()
        linked_user = User.objects.filter(username__in=[staff.phone, staff.email]).first()
        if linked_user:
            initial_username = linked_user.username
        else:
            initial_username = staff.phone

    form = StaffForm(request.POST or None, instance=staff, initial={'username': initial_username})

    if request.method == 'POST':
        if form.is_valid():
            staff = form.save()
            form.sync_user(staff)
            messages.success(request, 'Đã cập nhật nhân viên và tài khoản đăng nhập.')
            return redirect('staff_list')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin.')

    return render(request, 'staff/staff_form.html', {'form': form, 'mode': 'update', 'staff': staff})


@login_required
def staff_delete(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        # Cố gắng xóa user kèm theo nếu trùng username/phone
        User = get_user_model()
        try:
            user = User.objects.filter(username=staff.phone).first()
            if user:
                user.delete()
        except Exception:
            pass

        staff.delete()
        messages.success(request, 'Đã xóa nhân viên.')
        return redirect('staff_list')

    return render(request, 'staff/staff_confirm_delete.html', {'staff': staff})


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
