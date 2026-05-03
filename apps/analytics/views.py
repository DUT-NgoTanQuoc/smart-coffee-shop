import json

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.customers.models import Customer
from apps.orders.models import Order
from apps.products.models import Product
from apps.staff.models import Staff

from .ml_models import RevenuePredictor, StockPredictor, TrendAnalyzer
from .models import DailyStat


@login_required
def dashboard(request):
    """
    Dashboard chính - Tổng quan hệ thống
    Main dashboard - System overview
    - Barista: Redirect to barista dashboard (4-box layout)
    - Cashier: Redirect to create order page (POS)
    - Admin: Show admin dashboard (stats)
    """
    from django.core.cache import cache
    
    # Check user role (from CustomAccountBackend)
    user_role = getattr(request.user, 'role', None)
    
    if not request.user.is_superuser:
        if user_role == 'barista':
            return redirect('barista-dashboard')
        elif user_role == 'cashier':
            return redirect('create_order')
    
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
    ).count()
    
    # Lấy từ cache hoặc tính toán (cache 5 phút)
    cache_key = f'dashboard_analytics:{today.isoformat()}'
    analytics_data = cache.get(cache_key)
    
    if not analytics_data:
        # Cảnh báo nguyên liệu sắp hết
        stock_predictor = StockPredictor()
        low_stock_alerts = stock_predictor.get_low_stock_alerts()

        # Doanh thu 7 ngày qua (cho biểu đồ doanh thu)
        revenue_predictor = RevenuePredictor()
        revenue_data = revenue_predictor.predict(days_ahead=7)

        # Top 5 sản phẩm bán chạy (trong 7 ngày)
        trend_analyzer = TrendAnalyzer()
        bestsellers = trend_analyzer.get_bestselling_products(limit=5, period_days=7)
        peak_hours = trend_analyzer.get_peak_hours(period_days=30)
        category_performance = trend_analyzer.get_category_performance(period_days=30)
        customer_insights = trend_analyzer.get_customer_insights()
        revenue_summary = revenue_predictor.get_summary(days_ahead=30)

        # Chuẩn bị dữ liệu biểu đồ cho món bán chạy (best seller)
        bestseller_chart = {
            "labels": [item["product_name"] for item in bestsellers],
            "quantities": [item["quantity_sold"] for item in bestsellers],
            "revenues": [item["revenue"] for item in bestsellers],
        }

        # Chuẩn bị dữ liệu biểu đồ cho nguyên liệu (tồn kho & gợi ý nhập)
        ingredient_labels = [alert["ingredient"].name for alert in low_stock_alerts]
        ingredient_current_stock = [alert["current_stock"] for alert in low_stock_alerts]
        ingredient_recommended = [alert["recommended_quantity"] for alert in low_stock_alerts]
        ingredient_days_left = [alert["days_until_stockout"] or 0 for alert in low_stock_alerts]

        ingredient_chart = {
            "labels": ingredient_labels,
            "current_stock": ingredient_current_stock,
            "recommended_quantity": ingredient_recommended,
            "days_until_stockout": ingredient_days_left,
        }

        peak_hours_chart = {
            "labels": peak_hours.get("labels", []),
            "data": peak_hours.get("data", []),
            "peak_hour": peak_hours.get("peak_hour"),
            "peak_count": peak_hours.get("peak_count"),
        }

        category_chart = {
            "labels": category_performance.get("labels", []),
            "revenues": category_performance.get("revenues", []),
            "quantities": category_performance.get("quantities", []),
        }

        tier_distribution = customer_insights.get('tier_distribution', {})
        customer_tier_chart = {
            "labels": tier_distribution.get("labels", []),
            "data": tier_distribution.get("data", []),
        }
        
        analytics_data = {
            "low_stock_count": len(low_stock_alerts),
            "low_stock_alerts": low_stock_alerts[:5],
            "revenue_chart": json.dumps(revenue_data),
            "revenue_summary": revenue_summary,
            "bestsellers": bestsellers,
            "bestseller_chart": json.dumps(bestseller_chart),
            "ingredient_chart": json.dumps(ingredient_chart),
            "peak_hours_chart": json.dumps(peak_hours_chart),
            "category_chart": json.dumps(category_chart),
            "customer_tier_chart": json.dumps(customer_tier_chart),
        }
        
        # Cache 5 phút
        cache.set(cache_key, analytics_data, 300)

    # Backward-safe defaults when old cache payload exists.
    analytics_data.setdefault('revenue_summary', {'total_predicted': 0, 'average_daily': 0, 'trend': 'unknown', 'message': ''})
    analytics_data.setdefault('peak_hours_chart', json.dumps({'labels': [], 'data': []}))
    analytics_data.setdefault('category_chart', json.dumps({'labels': [], 'revenues': []}))
    analytics_data.setdefault('customer_tier_chart', json.dumps({'labels': [], 'data': []}))
    
    context = {
        "today": today,
        "today_revenue": today_stats.total_revenue,
        "today_orders": today_orders,
        "total_customers": Customer.objects.count(),
        "total_orders_all": Order.objects.count(),
        "total_revenue_all": Order.objects.filter(status='completed').aggregate(
            Sum('final_amount')
        )['final_amount__sum']
        or 0,
        "pending_orders": Order.objects.filter(status='pending').count(),
        "preparing_orders": Order.objects.filter(status='preparing').count(),
        "completed_orders": Order.objects.filter(status='completed').count(),
        "total_staff": Staff.objects.filter(is_active=True).count(),
        "total_products": Product.objects.count(),
        **analytics_data,  # Unpack cached data
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
        'prediction_data_json': json.dumps(prediction_data),
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
        'analysis_json': json.dumps(analysis),
        'period_days': period_days,
    }
    
    return render(request, 'analytics/trends.html', context)
