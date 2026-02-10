"""
Trend Analyzer - Phân tích xu hướng
Phân tích xu hướng bán hàng, giờ cao điểm, khách hàng, v.v.

Analyze sales trends, peak hours, customers, etc.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from collections import Counter


class TrendAnalyzer:
    """
    Class phân tích xu hướng kinh doanh
    Business trend analysis class
    """
    
    def __init__(self):
        self.analysis_period = 30  # Phân tích trong 30 ngày
    
    def get_bestselling_products(self, limit=10, period_days=30):
        """
        Lấy sản phẩm bán chạy nhất
        Get best-selling products
        
        Args:
            limit: Số lượng sản phẩm (default 10)
            period_days: Số ngày để phân tích (default 30)
        
        Returns:
            list: Danh sách sản phẩm bán chạy
        """
        from apps.orders.models import Order, OrderItem
        from django.utils import timezone
        from django.db.models import Sum, Count
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Lấy các order items trong khoảng thời gian
        bestsellers = OrderItem.objects.filter(
            order__status='completed',
            order__order_date__gte=start_date,
            order__order_date__lte=end_date
        ).values(
            'product__id',
            'product__name',
            'product__category__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal'),
            order_count=Count('order', distinct=True)
        ).order_by('-total_quantity')[:limit]
        
        result = []
        for item in bestsellers:
            result.append({
                'product_id': item['product__id'],
                'product_name': item['product__name'],
                'category': item['product__category__name'],
                'quantity_sold': item['total_quantity'],
                'revenue': float(item['total_revenue']),
                'order_count': item['order_count'],
            })
        
        return result
    
    def get_peak_hours(self, period_days=30):
        """
        Phân tích giờ cao điểm
        Analyze peak hours
        
        Args:
            period_days: Số ngày để phân tích
        
        Returns:
            dict: Dữ liệu giờ cao điểm cho heatmap
        """
        from apps.orders.models import Order
        from django.utils import timezone
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=period_days)
        
        orders = Order.objects.filter(
            status='completed',
            order_date__gte=start_date,
            order_date__lte=end_date
        )
        
        # Khởi tạo dict đếm theo giờ
        hour_counts = {hour: 0 for hour in range(24)}
        
        for order in orders:
            hour = order.order_date.hour
            hour_counts[hour] += 1
        
        # Chuẩn bị dữ liệu cho Chart.js
        result = {
            'labels': [f'{h:02d}:00' for h in range(24)],
            'data': [hour_counts[h] for h in range(24)],
            'peak_hour': max(hour_counts, key=hour_counts.get),
            'peak_count': max(hour_counts.values()),
        }
        
        return result
    
    def get_customer_insights(self):
        """
        Phân tích khách hàng
        Analyze customers
        
        Returns:
            dict: Thông tin khách hàng
        """
        from apps.customers.models import Customer
        from apps.orders.models import Order
        from django.db.models import Sum, Count
        
        # Top customers
        top_customers = Customer.objects.annotate(
            total_spent=Sum('orders__final_amount', filter=models.Q(orders__status='completed')),
            order_count=Count('orders', filter=models.Q(orders__status='completed'))
        ).filter(
            total_spent__isnull=False
        ).order_by('-total_spent')[:10]
        
        # Tier distribution
        tier_distribution = Customer.objects.values('tier').annotate(
            count=Count('id')
        ).order_by('-count')
        
        result = {
            'top_customers': [
                {
                    'name': c.name,
                    'phone': c.phone,
                    'tier': c.tier,
                    'total_spent': float(c.total_spent) if c.total_spent else 0,
                    'order_count': c.order_count,
                    'points': c.points,
                }
                for c in top_customers
            ],
            'tier_distribution': {
                'labels': [item['tier'] for item in tier_distribution],
                'data': [item['count'] for item in tier_distribution],
            },
            'total_customers': Customer.objects.count(),
        }
        
        return result
    
    def get_category_performance(self, period_days=30):
        """
        Phân tích hiệu suất theo danh mục
        Analyze performance by category
        
        Args:
            period_days: Số ngày để phân tích
        
        Returns:
            dict: Dữ liệu hiệu suất danh mục
        """
        from apps.orders.models import Order, OrderItem
        from django.utils import timezone
        from django.db.models import Sum, Count
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=period_days)
        
        category_stats = OrderItem.objects.filter(
            order__status='completed',
            order__order_date__gte=start_date,
            order__order_date__lte=end_date,
            product__category__isnull=False
        ).values(
            'product__category__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal'),
        ).order_by('-total_revenue')
        
        result = {
            'labels': [item['product__category__name'] for item in category_stats],
            'quantities': [item['total_quantity'] for item in category_stats],
            'revenues': [float(item['total_revenue']) for item in category_stats],
        }
        
        return result
    
    def get_sales_by_size(self, period_days=30):
        """
        Phân tích doanh số theo size
        Analyze sales by size
        
        Args:
            period_days: Số ngày để phân tích
        
        Returns:
            dict: Dữ liệu theo size
        """
        from apps.orders.models import Order, OrderItem
        from django.utils import timezone
        from django.db.models import Sum, Count
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=period_days)
        
        size_stats = OrderItem.objects.filter(
            order__status='completed',
            order__order_date__gte=start_date,
            order__order_date__lte=end_date
        ).values('size').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal'),
        ).order_by('size')
        
        result = {
            'labels': [item['size'] for item in size_stats],
            'quantities': [item['total_quantity'] for item in size_stats],
            'revenues': [float(item['total_revenue']) for item in size_stats],
        }
        
        return result
    
    def get_daily_revenue_trend(self, period_days=7):
        """
        Xu hướng doanh thu theo ngày
        Daily revenue trend
        
        Args:
            period_days: Số ngày để phân tích
        
        Returns:
            dict: Dữ liệu doanh thu theo ngày
        """
        from apps.analytics.models import DailyStat
        from django.utils import timezone
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        stats = DailyStat.objects.filter(
            stat_date__gte=start_date,
            stat_date__lte=end_date
        ).order_by('stat_date')
        
        result = {
            'labels': [stat.stat_date.strftime('%d/%m') for stat in stats],
            'revenues': [float(stat.total_revenue) for stat in stats],
            'orders': [stat.total_orders for stat in stats],
        }
        
        return result
    
    def get_complete_analysis(self):
        """
        Lấy toàn bộ phân tích
        Get complete analysis
        
        Returns:
            dict: Tất cả phân tích
        """
        return {
            'bestselling_products': self.get_bestselling_products(limit=5),
            'peak_hours': self.get_peak_hours(),
            'customer_insights': self.get_customer_insights(),
            'category_performance': self.get_category_performance(),
            'sales_by_size': self.get_sales_by_size(),
            'daily_revenue_trend': self.get_daily_revenue_trend(),
        }


# Import models để dùng trong query
from django.db import models
