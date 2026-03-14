from django.db import models


class Staff(models.Model):
    """
    Model nhân viên với phân quyền theo vai trò
    Staff model with role-based access
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
    role = models.CharField(
        max_length=50, 
        choices=ROLE_CHOICES,
        verbose_name='Vai trò'
    )
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Lương'
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
    Model chấm công - theo dõi giờ làm việc
    Work log model - attendance tracking
    """
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='work_logs',
        verbose_name='Nhân viên'
    )
    work_date = models.DateField(verbose_name='Ngày làm việc')
    check_in = models.TimeField(blank=True, null=True, verbose_name='Giờ vào')
    check_out = models.TimeField(blank=True, null=True, verbose_name='Giờ ra')
    hours_worked = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Số giờ làm'
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
        """Tính số giờ làm việc / Calculate working hours"""
        if self.check_in and self.check_out:
            from datetime import datetime, timedelta
            check_in_time = datetime.combine(datetime.today(), self.check_in)
            check_out_time = datetime.combine(datetime.today(), self.check_out)
            
            # Nếu check_out nhỏ hơn check_in (qua ngày)
            if check_out_time < check_in_time:
                check_out_time += timedelta(days=1)
            
            diff = check_out_time - check_in_time
            self.hours_worked = round(diff.total_seconds() / 3600, 2)
            self.save()
