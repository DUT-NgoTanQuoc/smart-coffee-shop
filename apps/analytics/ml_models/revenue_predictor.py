"""
Revenue Predictor - Dự đoán doanh thu
Sử dụng Linear Regression để dự đoán doanh thu trong tương lai

Using Linear Regression to predict future revenue
"""

from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
from sklearn.linear_model import LinearRegression


class RevenuePredictor:
    """
    Class dự đoán doanh thu dựa trên dữ liệu lịch sử
    Revenue prediction class based on historical data
    """
    
    def __init__(self):
        self.model = LinearRegression()
    
    def get_historical_data(self, days=30):
        """
        Lấy dữ liệu lịch sử từ DailyStat
        Get historical data from DailyStat
        
        Args:
            days: Số ngày lịch sử để lấy (default 30)
        
        Returns:
            tuple: (dates, revenues)
        """
        from apps.analytics.models import DailyStat
        from django.utils import timezone
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        stats = DailyStat.objects.filter(
            stat_date__gte=start_date,
            stat_date__lte=end_date
        ).order_by('stat_date')
        
        if not stats.exists():
            return None, None
        
        dates = []
        revenues = []
        
        for stat in stats:
            dates.append(stat.stat_date)
            revenues.append(float(stat.total_revenue))
        
        return dates, revenues
    
    def train(self, dates, revenues):
        """
        Huấn luyện model với dữ liệu lịch sử
        Train model with historical data
        
        Args:
            dates: List of dates
            revenues: List of revenues
        """
        if not dates or not revenues:
            return False
        
        # Chuyển đổi ngày thành số (số ngày từ ngày đầu tiên)
        first_date = dates[0]
        X = np.array([(d - first_date).days for d in dates]).reshape(-1, 1)
        y = np.array(revenues)
        
        self.model.fit(X, y)
        self.first_date = first_date
        return True
    
    def predict(self, days_ahead=7):
        """
        Dự đoán doanh thu cho N ngày tới
        Predict revenue for next N days
        
        Args:
            days_ahead: Số ngày cần dự đoán (default 7)
        
        Returns:
            dict: Dữ liệu dự đoán cho Chart.js
        """
        from django.utils import timezone
        
        # Lấy dữ liệu lịch sử và train model
        dates, revenues = self.get_historical_data()
        
        if not dates or not revenues:
            return {
                'labels': [],
                'historical': [],
                'predicted': [],
                'message': 'Chưa có đủ dữ liệu lịch sử'
            }
        
        if not self.train(dates, revenues):
            return {
                'labels': [],
                'historical': [],
                'predicted': [],
                'message': 'Không thể huấn luyện model'
            }
        
        # Tạo dự đoán
        today = timezone.now().date()
        prediction_dates = [today + timedelta(days=i) for i in range(1, days_ahead + 1)]
        
        # Chuyển đổi ngày thành số
        X_pred = np.array([(d - self.first_date).days for d in prediction_dates]).reshape(-1, 1)
        predictions = self.model.predict(X_pred)
        
        # Đảm bảo predictions không âm
        predictions = np.maximum(predictions, 0)
        
        # Chuẩn bị dữ liệu cho Chart.js
        result = {
            'labels': [d.strftime('%d/%m/%Y') for d in dates] + 
                     [d.strftime('%d/%m/%Y') for d in prediction_dates],
            'historical': revenues + [None] * len(predictions),
            'predicted': [None] * len(revenues) + predictions.tolist(),
            'message': f'Dự đoán doanh thu {days_ahead} ngày tới'
        }
        
        return result
    
    def get_summary(self, days_ahead=7):
        """
        Lấy tóm tắt dự đoán
        Get prediction summary
        
        Returns:
            dict: Tóm tắt dự đoán
        """
        prediction_data = self.predict(days_ahead)
        
        if not prediction_data['predicted'] or all(p is None for p in prediction_data['predicted']):
            return {
                'total_predicted': 0,
                'average_daily': 0,
                'trend': 'unknown',
                'message': 'Chưa có dữ liệu dự đoán'
            }
        
        # Lọc bỏ giá trị None
        predicted_values = [p for p in prediction_data['predicted'] if p is not None]
        
        total_predicted = sum(predicted_values)
        average_daily = total_predicted / len(predicted_values) if predicted_values else 0
        
        # Xác định xu hướng
        historical_values = [h for h in prediction_data['historical'] if h is not None]
        if historical_values and predicted_values:
            avg_historical = sum(historical_values[-7:]) / min(7, len(historical_values))
            if average_daily > avg_historical * 1.1:
                trend = 'tăng'
            elif average_daily < avg_historical * 0.9:
                trend = 'giảm'
            else:
                trend = 'ổn định'
        else:
            trend = 'unknown'
        
        return {
            'total_predicted': round(total_predicted, 2),
            'average_daily': round(average_daily, 2),
            'trend': trend,
            'days_ahead': days_ahead,
            'message': f'Dự đoán {days_ahead} ngày: Xu hướng {trend}'
        }
