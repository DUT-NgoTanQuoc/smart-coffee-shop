import json
from collections import defaultdict
from datetime import date as dt_date
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import ShiftAssignmentForm, StaffForm
from .models import ShiftAssignment, ShiftRule, Staff, WorkLog

SHIFT_ORDER = ['morning', 'afternoon', 'evening']


def _safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_decimal(value):
    if value in (None, ''):
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _json_error(message, status=400, extra=None):
    payload = {'ok': False, 'message': message}
    if extra:
        payload.update(extra)
    return JsonResponse(payload, status=status)


def _parse_request_payload(request):
    if request.content_type and 'application/json' in request.content_type:
        try:
            raw = request.body.decode('utf-8') if request.body else '{}'
            return json.loads(raw)
        except Exception:
            return {}
    return request.POST.dict()


def _build_payroll_summary(month, year):
    assignments = (
        ShiftAssignment.objects.filter(work_date__month=month, work_date__year=year)
        .select_related('staff')
        .order_by('-work_date', 'shift', 'staff__name')
    )

    work_hours_map = {
        row['staff_id']: Decimal(str(row['total_hours'] or 0))
        for row in (
            WorkLog.objects.filter(work_date__month=month, work_date__year=year)
            .values('staff_id')
            .annotate(total_hours=Sum('hours_worked'))
        )
    }

    payroll_map = defaultdict(
        lambda: {
            'staff': None,
            'assigned_hours': Decimal('0'),
            'actual_hours': Decimal('0'),
            'weighted_rate_total': Decimal('0'),
            'total_pay': Decimal('0'),
            'shift_count': 0,
        }
    )

    for assignment in assignments:
        row = payroll_map[assignment.staff_id]
        row['staff'] = assignment.staff
        hours = Decimal(str(assignment.planned_hours or 0))
        rate = Decimal(str(assignment.staff.salary or 0))
        pay = hours * rate

        row['assigned_hours'] += hours
        row['weighted_rate_total'] += rate * hours
        row['total_pay'] += pay
        row['shift_count'] += 1

    payroll_summary = []
    total_assigned_hours = Decimal('0')
    total_actual_hours = Decimal('0')
    total_payroll = Decimal('0')

    for staff_id, row in payroll_map.items():
        assigned_hours = row['assigned_hours']
        actual_hours = work_hours_map.get(staff_id, Decimal('0'))
        avg_rate = Decimal(str(row['staff'].salary or 0)).quantize(Decimal('0.01'))

        row['actual_hours'] = actual_hours
        row['avg_hourly_rate'] = avg_rate
        row['total_pay'] = row['total_pay'].quantize(Decimal('0.01'))

        total_assigned_hours += assigned_hours
        total_actual_hours += actual_hours
        total_payroll += row['total_pay']
        payroll_summary.append(row)

    payroll_summary.sort(key=lambda x: x['total_pay'], reverse=True)

    return {
        'payroll_summary': payroll_summary,
        'total_assigned_hours': total_assigned_hours,
        'total_actual_hours': total_actual_hours,
        'total_payroll': total_payroll,
    }


def _get_shift_rules_map():
    ShiftRule.ensure_defaults()
    rules = list(ShiftRule.objects.filter(is_active=True).order_by('sort_order', 'shift'))
    by_shift = {rule.shift: rule for rule in rules}
    return rules, by_shift


def _serialize_assignment(assignment):
    return {
        'id': assignment.id,
        'staff_id': assignment.staff_id,
        'staff_name': assignment.staff.name,
        'work_date': assignment.work_date.isoformat(),
        'shift': assignment.shift,
        'shift_display': assignment.get_shift_display(),
        'start_time': assignment.start_time.strftime('%H:%M') if assignment.start_time else '',
        'end_time': assignment.end_time.strftime('%H:%M') if assignment.end_time else '',
        'planned_hours': float(assignment.planned_hours or 0),
        'hourly_rate': float(assignment.effective_hourly_rate or 0),
        'estimated_pay': float(assignment.estimated_pay or 0),
        'note': assignment.note or '',
    }


def _staffing_warning(total_count, min_staff, max_staff):
    if total_count < min_staff:
        missing = min_staff - total_count
        return 'short', f'Thiếu {missing} người so với tối thiểu {min_staff}.'
    if total_count > max_staff:
        extra = total_count - max_staff
        return 'excess', f'Dư {extra} người so với tối đa {max_staff}.'
    return 'ok', 'Đủ nhân sự.'


@login_required
def staff_list(request):
    """Danh sách nhân viên."""
    staff_members = Staff.objects.all().order_by('name')

    role = request.GET.get('role')
    if role:
        staff_members = staff_members.filter(role=role)

    is_active = request.GET.get('is_active')
    if is_active:
        staff_members = staff_members.filter(is_active=is_active == 'true')

    return render(request, 'staff/staff_list.html', {'staff_members': staff_members})


@login_required
def staff_payroll_summary(request):
    """Tổng hợp lương theo giờ theo tháng."""
    today = timezone.now().date()
    month = _safe_int(request.GET.get('month'), today.month)
    year = _safe_int(request.GET.get('year'), today.year)

    current_year = today.year
    context = {
        'month': month,
        'year': year,
        'months': list(range(1, 13)),
        'years': list(range(current_year - 2, current_year + 2)),
        'monthly_totals': ShiftAssignment.monthly_shift_totals(year=year, month=month),
        **_build_payroll_summary(month, year),
    }
    return render(request, 'staff/staff_payroll_summary.html', context)


@login_required
def shift_assignment_delete(request, assignment_id):
    assignment = get_object_or_404(ShiftAssignment, id=assignment_id)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Đã xóa phân công ca.')

    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('staff_list')


@login_required
def staff_detail(request, staff_id):
    """Chi tiết nhân viên."""
    staff = get_object_or_404(Staff, id=staff_id)
    work_logs = staff.work_logs.all().order_by('-work_date')[:30]
    recent_assignments = staff.shift_assignments.all().order_by('-work_date', 'shift')[:30]

    context = {
        'staff': staff,
        'work_logs': work_logs,
        'recent_assignments': recent_assignments,
    }

    return render(request, 'staff/staff_detail.html', context)


@login_required
def staff_create(request):
    """Tạo nhân viên và tài khoản đăng nhập."""
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
    """Cập nhật nhân viên và tài khoản đăng nhập."""
    staff = get_object_or_404(Staff, id=staff_id)
    previous_is_active = staff.is_active

    initial_username = ''
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute('SELECT username FROM accounts WHERE staff_id = %s', [staff_id])
        result = cursor.fetchone()
        if result:
            initial_username = result[0]

    if not initial_username:
        user_model = get_user_model()
        linked_user = user_model.objects.filter(username__in=[staff.phone, staff.email]).first()
        if linked_user:
            initial_username = linked_user.username
        else:
            initial_username = staff.phone

    form = StaffForm(request.POST or None, instance=staff, initial={'username': initial_username})

    if request.method == 'POST':
        if form.is_valid():
            staff = form.save()
            if previous_is_active and not staff.is_active:
                today = timezone.localdate()
                future_assignments = ShiftAssignment.objects.filter(staff=staff, work_date__gt=today)
                deleted_count = future_assignments.count()
                if deleted_count:
                    future_assignments.delete()
                    messages.info(
                        request,
                        f'Đã ngưng làm và xóa {deleted_count} ca phân công trong tương lai.',
                    )
            form.sync_user(staff)
            messages.success(request, 'Đã cập nhật nhân viên và tài khoản đăng nhập.')
            return redirect('staff_list')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin.')

    return render(request, 'staff/staff_form.html', {'form': form, 'mode': 'update', 'staff': staff})


@login_required
def staff_delete(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        user_model = get_user_model()
        try:
            user = user_model.objects.filter(username=staff.phone).first()
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
    """Danh sách chấm công."""
    today = timezone.now().date()
    month = _safe_int(request.GET.get('month'), today.month)
    year = _safe_int(request.GET.get('year'), today.year)

    work_logs = (
        WorkLog.objects.filter(work_date__month=month, work_date__year=year)
        .select_related('staff')
        .order_by('-work_date')
    )

    current_year = today.year
    context = {
        'work_logs': work_logs,
        'month': month,
        'year': year,
        'months': list(range(1, 13)),
        'years': list(range(current_year - 2, current_year + 2)),
    }

    return render(request, 'staff/attendance_list.html', context)


@login_required
def schedule_calendar(request):
    """Render scheduling page (calendar + side panel)."""
    rules, _ = _get_shift_rules_map()

    staff_qs = Staff.objects.filter(is_active=True).order_by('role', 'name')
    staff_by_role = []
    for role_value, role_label in Staff.ROLE_CHOICES:
        grouped = [staff for staff in staff_qs if staff.role == role_value]
        if grouped:
            staff_by_role.append({'role': role_value, 'label': role_label, 'items': grouped})

    shift_rules_payload = {
        rule.shift: {
            'start_time': rule.start_time.strftime('%H:%M'),
            'end_time': rule.end_time.strftime('%H:%M'),
            'min_staff': rule.min_staff,
            'max_staff': rule.max_staff,
            'shift_display': rule.get_shift_display(),
        }
        for rule in rules
    }

    assignment_form = ShiftAssignmentForm(initial={'work_date': timezone.localdate()})
    assignment_form.fields['staff'].queryset = staff_qs

    return render(
        request,
        'staff/schedule_calendar.html',
        {
            'assignment_form': assignment_form,
            'staff_choices': staff_qs,
            'staff_by_role': staff_by_role,
            'shift_rules': rules,
            'shift_rules_json': json.dumps(shift_rules_payload, ensure_ascii=False),
        },
    )


@login_required
@require_GET
def schedule_api_events(request):
    """
    JSON events for FullCalendar.
    - 3 fixed shifts/day
    - staff filter
    - warning thiếu/dư người based on ShiftRule min/max
    """
    _, rules_map = _get_shift_rules_map()

    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    staff_filter_id = _safe_int(request.GET.get('staff_id'), None)

    try:
        if start_str:
            start_date = dt_date.fromisoformat(start_str[:10])
        else:
            today = timezone.localdate()
            start_date = dt_date(today.year, today.month, 1)

        if end_str:
            end_exclusive = dt_date.fromisoformat(end_str[:10])
        else:
            end_exclusive = start_date + timedelta(days=42)
    except ValueError:
        return _json_error('Khoảng ngày không hợp lệ.')

    all_assignments = (
        ShiftAssignment.objects.filter(work_date__gte=start_date, work_date__lt=end_exclusive)
        .select_related('staff')
        .order_by('work_date', 'shift', 'staff__name')
    )

    visible_assignments = all_assignments
    if staff_filter_id:
        visible_assignments = visible_assignments.filter(staff_id=staff_filter_id)

    all_count_map = defaultdict(int)
    role_count_map = defaultdict(lambda: {'cashier': 0, 'barista': 0})
    for assignment in all_assignments:
        all_count_map[(assignment.work_date, assignment.shift)] += 1
        role = assignment.staff.role
        if role in role_count_map[(assignment.work_date, assignment.shift)]:
            role_count_map[(assignment.work_date, assignment.shift)][role] += 1

    visible_group = defaultdict(list)
    for assignment in visible_assignments:
        visible_group[(assignment.work_date, assignment.shift)].append(assignment)

    events = []
    current_day = start_date
    while current_day < end_exclusive:
        for shift in SHIFT_ORDER:
            rule = rules_map.get(shift)
            if not rule:
                continue

            key = (current_day, shift)
            total_count = all_count_map.get(key, 0)
            shown_items = visible_group.get(key, [])
            shown_names = [item.staff.name for item in shown_items]

            status, warning = _staffing_warning(total_count, rule.min_staff, rule.max_staff)

            role_counts = role_count_map.get(key, {'cashier': 0, 'barista': 0})
            missing_roles = []
            if role_counts.get('cashier', 0) < 1:
                missing_roles.append('thiếu thu ngân')
            if role_counts.get('barista', 0) < 1:
                missing_roles.append('thiếu barista')
            if missing_roles:
                status = 'short'
                warning = ' / '.join(missing_roles)

            if shown_names:
                title_names = ', '.join(shown_names)
            elif staff_filter_id and total_count > 0:
                title_names = '(không khớp bộ lọc)'
            else:
                title_names = 'Trống'

            events.append(
                {
                    'id': f'{current_day.isoformat()}-{shift}',
                    'title': f'{rule.get_shift_display()}: {title_names}',
                    'start': f"{current_day.isoformat()}T{rule.start_time.strftime('%H:%M:%S')}",
                    'end': f"{current_day.isoformat()}T{rule.end_time.strftime('%H:%M:%S')}",
                    'allDay': False,
                    'display': 'block',
                    'extendedProps': {
                        'work_date': current_day.isoformat(),
                        'shift': shift,
                        'shift_display': rule.get_shift_display(),
                        'min_staff': rule.min_staff,
                        'max_staff': rule.max_staff,
                        'total_count': total_count,
                        'status': status,
                        'warning': warning,
                        'staff_names': shown_names,
                        'assignments': [_serialize_assignment(item) for item in shown_items],
                        'role_counts': role_counts,
                    },
                }
            )

        current_day += timedelta(days=1)

    return JsonResponse(events, safe=False)


@login_required
@require_POST
def schedule_api_create(request):
    payload = _parse_request_payload(request)
    form = ShiftAssignmentForm(payload)
    form.fields['staff'].queryset = Staff.objects.filter(is_active=True).order_by('name')

    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    assignment = form.save()
    return JsonResponse({'ok': True, 'message': 'Đã thêm phân ca.', 'assignment': _serialize_assignment(assignment)})


@login_required
@require_POST
def schedule_api_update(request, assignment_id):
    assignment = get_object_or_404(ShiftAssignment, pk=assignment_id)
    payload = _parse_request_payload(request)

    merged = {
        'staff': payload.get('staff', assignment.staff_id),
        'work_date': payload.get('work_date', assignment.work_date.isoformat()),
        'shift': payload.get('shift', assignment.shift),
        'start_time': payload.get('start_time', assignment.start_time.strftime('%H:%M') if assignment.start_time else ''),
        'end_time': payload.get('end_time', assignment.end_time.strftime('%H:%M') if assignment.end_time else ''),
        'hourly_rate': payload.get(
            'hourly_rate',
            assignment.hourly_rate if assignment.hourly_rate is not None else '',
        ),
        'note': payload.get('note', assignment.note or ''),
    }

    form = ShiftAssignmentForm(merged, instance=assignment)
    form.fields['staff'].queryset = Staff.objects.filter(is_active=True).order_by('name') | Staff.objects.filter(
        pk=assignment.staff_id
    )

    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    updated_assignment = form.save()
    return JsonResponse(
        {'ok': True, 'message': 'Đã cập nhật phân ca.', 'assignment': _serialize_assignment(updated_assignment)}
    )


@login_required
@require_POST
def schedule_api_delete(request, assignment_id):
    assignment = get_object_or_404(ShiftAssignment, pk=assignment_id)
    assignment.delete()
    return JsonResponse({'ok': True, 'message': 'Đã xóa phân ca.'})


# Backward-compatible aliases for existing routes
schedule_events = schedule_api_events
schedule_event_delete = schedule_api_delete
