from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DailyStat
from .ml_models import RevenuePredictor, StockPredictor, TrendAnalyzer
from apps.orders.models import Order
from apps.customers.models import Customer
from apps.ingredients.models import Ingredient
from apps.core.models import Account
from django.utils import timezone
from datetime import timedelta


@login_required
def dashboard(request):
    """
    Dashboard chính - Tổng quan hệ thống
    Main dashboard - System overview
    - Barista: Redirect to barista dashboard (4-box layout)
    - Cashier: Redirect to create order page (POS)
    - Admin: Show admin dashboard (stats)
    """
    # Check user role
    if request.user.is_superuser:
        # Admin stays on admin dashboard
        pass
    else:
        try:
            staff = Account.objects.get(username=request.user.username)
            if staff.role_id == 3:  # Barista
                return redirect('barista-dashboard')
            elif staff.role_id == 2:  # Cashier
                return redirect('create_order')
        except Account.DoesNotExist:
            # User không có Account record, hiển thị admin dashboard
            pass
    
    today = timezone.now().date()
    
    # Thống kê hôm nay
    today_stats, _ = DailyStat.objects.get_or_create(
        stat_date=today,
        defaults={'total_revenue': 0, 'total_orders': 0, 'total_customers': 0}
    )
    
    # Đơn hàng hôm nay
    today_orders = Order.objects.filter(
        order_date__date=today,
        status='completed'
    )
    
    # Cảnh báo nguyên liệu sắp hết
    stock_predictor = StockPredictor()
    low_stock_alerts = stock_predictor.get_low_stock_alerts()
    
    # Doanh thu 7 ngày qua
    revenue_predictor = RevenuePredictor()
    revenue_data = revenue_predictor.predict(days_ahead=7)
    
    # Top 5 sản phẩm bán chạy
    trend_analyzer = TrendAnalyzer()
    bestsellers = trend_analyzer.get_bestselling_products(limit=5, period_days=7)
    
    context = {
        'today_revenue': today_stats.total_revenue,
        'today_orders': today_orders.count(),
        'low_stock_count': len(low_stock_alerts),
        'total_customers': Customer.objects.count(),
        'low_stock_alerts': low_stock_alerts[:5],  # Top 5 cảnh báo
        'revenue_chart': revenue_data,
        'bestsellers': bestsellers,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def revenue_forecast(request):
    """
    Dự đoán doanh thu
    Revenue forecast
    """
    days_ahead = int(request.GET.get('days', 7))
    
    revenue_predictor = RevenuePredictor()
    prediction_data = revenue_predictor.predict(days_ahead=days_ahead)
    summary = revenue_predictor.get_summary(days_ahead=days_ahead)
    
    context = {
        'prediction_data': prediction_data,
        'summary': summary,
        'days_ahead': days_ahead,
    }
    
    return render(request, 'analytics/revenue_forecast.html', context)


@login_required
def stock_prediction(request):
    """
    Dự đoán tồn kho
    Stock prediction
    """
    stock_predictor = StockPredictor()
    predictions = stock_predictor.predict_all_ingredients()
    summary = stock_predictor.get_summary()
    
    context = {
        'predictions': predictions,
        'summary': summary,
    }
    
    return render(request, 'analytics/stock_prediction.html', context)


@login_required
def trends(request):
    """
    Phân tích xu hướng
    Trend analysis
    """
    period_days = int(request.GET.get('days', 30))
    
    trend_analyzer = TrendAnalyzer()
    analysis = trend_analyzer.get_complete_analysis()
    
    context = {
        'analysis': analysis,
        'period_days': period_days,
    }
    
    return render(request, 'analytics/trends.html', context)
