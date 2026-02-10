from django.db import models


class DailyStat(models.Model):
    """
    Model thống kê hàng ngày
    Daily statistics model
    """
    stat_date = models.DateField(unique=True, verbose_name='Ngày')
    total_revenue = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Doanh thu'
    )
    total_orders = models.IntegerField(default=0, verbose_name='Số đơn hàng')
    total_customers = models.IntegerField(default=0, verbose_name='Số khách hàng')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'daily_stats'
        verbose_name = 'Thống kê ngày'
        verbose_name_plural = 'Thống kê ngày'
        ordering = ['-stat_date']

    def __str__(self):
        return f'{self.stat_date} - {self.total_revenue}đ'
