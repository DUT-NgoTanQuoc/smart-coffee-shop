from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db import models
from django.db.models import Count, Sum


class Staff(models.Model):
    """
    Staff model.
    NOTE: If your real employee model has a different name, replace `Staff`
    with your model (e.g. Employee) in ShiftAssignment ForeignKey.
    """

    ROLE_CHOICES = [
        ('manager', 'Quản lý'),
        ('cashier', 'Thu ngân'),
        ('barista', 'Barista'),
        ('parttime', 'Part-time'),
    ]

    name = models.CharField(max_length=100, verbose_name='Tên nhân viên')
    phone = models.CharField(max_length=20, unique=True, verbose_name='Số điện thoại')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name='Vai trò')
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Lương',
    )
    hire_date = models.DateField(verbose_name='Ngày vào làm')
    is_active = models.BooleanField(default=True, verbose_name='Đang làm việc')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'staff'
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_role_display()})'


class WorkLog(models.Model):
    """
    Attendance model - used for real worked hours.
    """

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='work_logs',
        verbose_name='Nhân viên',
    )
    work_date = models.DateField(verbose_name='Ngày làm việc')
    check_in = models.TimeField(blank=True, null=True, verbose_name='Giờ vào')
    check_out = models.TimeField(blank=True, null=True, verbose_name='Giờ ra')
    hours_worked = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Số giờ làm',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'work_logs'
        verbose_name = 'Chấm công'
        verbose_name_plural = 'Chấm công'
        ordering = ['-work_date']
        unique_together = ['staff', 'work_date']

    def __str__(self):
        return f'{self.staff.name} - {self.work_date}'

    def calculate_hours(self):
        if self.check_in and self.check_out:
            check_in_time = datetime.combine(datetime.today(), self.check_in)
            check_out_time = datetime.combine(datetime.today(), self.check_out)
            if check_out_time < check_in_time:
                check_out_time += timedelta(days=1)
            diff = check_out_time - check_in_time
            self.hours_worked = round(diff.total_seconds() / 3600, 2)
            self.save(update_fields=['hours_worked'])


class ShiftRule(models.Model):
    """
    Shift configuration:
    - fixed shift slots (morning/afternoon/evening)
    - required headcount boundaries for warning.
    """

    SHIFT_CHOICES = [
        ('morning', 'Ca sáng'),
        ('afternoon', 'Ca chiều'),
        ('evening', 'Ca tối'),
    ]

    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, unique=True, verbose_name='Ca')
    start_time = models.TimeField(verbose_name='Giờ bắt đầu')
    end_time = models.TimeField(verbose_name='Giờ kết thúc')
    min_staff = models.PositiveSmallIntegerField(default=2, verbose_name='Tối thiểu nhân sự')
    max_staff = models.PositiveSmallIntegerField(default=4, verbose_name='Tối đa nhân sự')
    sort_order = models.PositiveSmallIntegerField(default=1, verbose_name='Thứ tự hiển thị')
    is_active = models.BooleanField(default=True, verbose_name='Đang áp dụng')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật lúc')

    class Meta:
        db_table = 'staff_shift_rules'
        verbose_name = 'Cấu hình ca'
        verbose_name_plural = 'Cấu hình ca'
        ordering = ['sort_order', 'shift']

    def __str__(self):
        return f'{self.get_shift_display()} ({self.start_time}-{self.end_time})'

    @classmethod
    def ensure_defaults(cls):
        defaults = [
            ('morning', time(7, 0), time(12, 0), 2, 4, 1),
            ('afternoon', time(13, 0), time(18, 0), 2, 4, 2),
            ('evening', time(18, 0), time(22, 0), 1, 3, 3),
        ]
        for shift, start_time, end_time, min_staff, max_staff, sort_order in defaults:
            cls.objects.get_or_create(
                shift=shift,
                defaults={
                    'start_time': start_time,
                    'end_time': end_time,
                    'min_staff': min_staff,
                    'max_staff': max_staff,
                    'sort_order': sort_order,
                    'is_active': True,
                },
            )


class ShiftAssignment(models.Model):
    """
    Planned shift assignment for staff.
    """

    SHIFT_CHOICES = ShiftRule.SHIFT_CHOICES
    DEFAULT_SHIFT_TIME = {
        'morning': (time(7, 0), time(12, 0)),
        'afternoon': (time(13, 0), time(18, 0)),
        'evening': (time(18, 0), time(22, 0)),
    }

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='shift_assignments',
        verbose_name='Nhân viên',
    )
    work_date = models.DateField(verbose_name='Ngày làm việc')
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, verbose_name='Ca làm')
    start_time = models.TimeField(blank=True, null=True, verbose_name='Giờ bắt đầu')
    end_time = models.TimeField(blank=True, null=True, verbose_name='Giờ kết thúc')
    planned_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Số giờ dự kiến',
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Lương theo giờ',
    )
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'staff_shift_assignments'
        verbose_name = 'Phân công ca'
        verbose_name_plural = 'Phân công ca'
        ordering = ['-work_date', 'shift', 'staff__name']
        unique_together = ['staff', 'work_date', 'shift']
        indexes = [
            models.Index(fields=['work_date', 'shift']),
            models.Index(fields=['staff', 'work_date']),
        ]

    def __str__(self):
        return f'{self.staff.name} - {self.work_date} - {self.get_shift_display()}'

    def _calculate_planned_hours(self):
        if not self.start_time or not self.end_time:
            return None
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        diff = end_dt - start_dt
        return round(diff.total_seconds() / 3600, 2)

    def save(self, *args, **kwargs):
        ShiftRule.ensure_defaults()

        rule = ShiftRule.objects.filter(shift=self.shift, is_active=True).first()
        if rule:
            if not self.start_time:
                self.start_time = rule.start_time
            if not self.end_time:
                self.end_time = rule.end_time
        elif self.shift in self.DEFAULT_SHIFT_TIME:
            default_start, default_end = self.DEFAULT_SHIFT_TIME[self.shift]
            if not self.start_time:
                self.start_time = default_start
            if not self.end_time:
                self.end_time = default_end

        calculated_hours = self._calculate_planned_hours()
        if calculated_hours is not None:
            self.planned_hours = calculated_hours

        super().save(*args, **kwargs)

    @property
    def effective_hourly_rate(self):
        if self.staff and self.staff.role == 'manager':
            return Decimal('0')
        if self.hourly_rate is not None and self.hourly_rate > 0:
            return self.hourly_rate
        if self.staff.salary:
            return Decimal(self.staff.salary) / Decimal('208')
        return Decimal('0')

    @property
    def estimated_pay(self):
        if not self.planned_hours:
            return Decimal('0')
        return Decimal(self.planned_hours) * self.effective_hourly_rate

    @classmethod
    def monthly_shift_totals(cls, year: int, month: int):
        """
        Helper for payroll integration:
        return total shifts/hours/estimated pay per staff for a month.
        """
        qs = cls.objects.filter(work_date__year=year, work_date__month=month).select_related('staff')
        rows = (
            qs.values('staff_id', 'staff__name')
            .annotate(total_shifts=Count('id'), total_hours=Sum('planned_hours'))
            .order_by('-total_shifts', 'staff__name')
        )

        result = []
        for row in rows:
            staff_id = row['staff_id']
            staff_qs = qs.filter(staff_id=staff_id)
            estimated_pay = sum((item.estimated_pay for item in staff_qs), Decimal('0'))
            result.append(
                {
                    'staff_id': staff_id,
                    'staff_name': row['staff__name'],
                    'total_shifts': row['total_shifts'] or 0,
                    'total_hours': row['total_hours'] or Decimal('0'),
                    'estimated_pay': estimated_pay,
                }
            )
        return result
