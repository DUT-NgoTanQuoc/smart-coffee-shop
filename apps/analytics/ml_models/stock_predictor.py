"""
Stock Predictor - Dự đoán tồn kho
Tính toán mức tiêu thụ trung bình và dự đoán khi nào hết hàng

Calculate average consumption and predict stock depletion
"""

from datetime import datetime, timedelta
from decimal import Decimal


class StockPredictor:
    """
    Class dự đoán tồn kho và đề xuất nhập hàng
    Stock prediction and restock recommendation class
    """
    
    def __init__(self):
        self.consumption_period = 7  # Tính mức tiêu thụ trong 7 ngày
    
    def calculate_daily_consumption(self, ingredient):
        """
        Tính mức tiêu thụ trung bình hàng ngày
        Calculate average daily consumption
        
        Args:
            ingredient: Ingredient object
        
        Returns:
            float: Mức tiêu thụ trung bình/ngày
        """
        from apps.orders.models import Order, OrderItem
        from apps.products.models import Recipe
        from django.utils import timezone
        
        # Lấy đơn hàng hoàn thành trong N ngày qua
        end_date = timezone.now()
        start_date = end_date - timedelta(days=self.consumption_period)
        
        completed_orders = Order.objects.filter(
            status='completed',
            order_date__gte=start_date,
            order_date__lte=end_date
        )
        
        total_consumed = 0
        
        # Tính tổng lượng nguyên liệu đã dùng
        for order in completed_orders:
            for item in order.items.all():
                # Lấy công thức của sản phẩm
                recipes = Recipe.objects.filter(
                    product=item.product,
                    ingredient=ingredient
                )
                
                for recipe in recipes:
                    # Tính lượng nguyên liệu cần cho item này
                    quantity_per_item = recipe.get_quantity(item.size)
                    total_consumed += float(quantity_per_item) * item.quantity
        
        # Tính trung bình mỗi ngày
        daily_consumption = total_consumed / self.consumption_period if self.consumption_period > 0 else 0
        
        return daily_consumption
    
    def predict_stockout_date(self, ingredient):
        """
        Dự đoán ngày hết hàng
        Predict when stock will run out
        
        Args:
            ingredient: Ingredient object
        
        Returns:
            tuple: (days_until_stockout, stockout_date)
        """
        from django.utils import timezone
        
        daily_consumption = self.calculate_daily_consumption(ingredient)
        
        if daily_consumption <= 0:
            return None, None
        
        current_stock = float(ingredient.quantity)
        days_until_stockout = current_stock / daily_consumption
        
        stockout_date = timezone.now().date() + timedelta(days=int(days_until_stockout))
        
        return round(days_until_stockout, 1), stockout_date
    
    def get_priority_level(self, days_until_stockout):
        """
        Xác định mức độ ưu tiên nhập hàng
        Determine restock priority level
        
        Args:
            days_until_stockout: Số ngày đến khi hết hàng
        
        Returns:
            str: Mức độ ưu tiên (HIGH, MEDIUM, LOW)
        """
        if days_until_stockout is None:
            return 'LOW'
        
        if days_until_stockout <= 3:
            return 'HIGH'
        elif days_until_stockout <= 7:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def get_restock_recommendation(self, ingredient):
        """
        Đề xuất số lượng cần nhập
        Get restock quantity recommendation
        
        Args:
            ingredient: Ingredient object
        
        Returns:
            float: Số lượng đề xuất nhập
        """
        daily_consumption = self.calculate_daily_consumption(ingredient)
        
        # Đề xuất nhập đủ cho 30 ngày
        recommended_quantity = daily_consumption * 30
        
        # Trừ đi lượng hiện tại
        current_stock = float(ingredient.quantity)
        needed = recommended_quantity - current_stock
        
        return max(0, round(needed, 2))
    
    def predict_all_ingredients(self):
        """
        Dự đoán cho tất cả nguyên liệu
        Predict for all ingredients
        
        Returns:
            list: Danh sách dự đoán cho từng nguyên liệu
        """
        from apps.ingredients.models import Ingredient
        
        ingredients = Ingredient.objects.all()
        predictions = []
        
        for ingredient in ingredients:
            daily_consumption = self.calculate_daily_consumption(ingredient)
            days_until_stockout, stockout_date = self.predict_stockout_date(ingredient)
            priority = self.get_priority_level(days_until_stockout)
            recommended_quantity = self.get_restock_recommendation(ingredient)
            
            predictions.append({
                'ingredient': ingredient,
                'current_stock': float(ingredient.quantity),
                'unit': ingredient.unit,
                'daily_consumption': round(daily_consumption, 2),
                'days_until_stockout': days_until_stockout,
                'stockout_date': stockout_date,
                'priority': priority,
                'recommended_quantity': recommended_quantity,
            })
        
        # Sắp xếp theo mức độ ưu tiên
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        predictions.sort(key=lambda x: (
            priority_order.get(x['priority'], 3),
            x['days_until_stockout'] if x['days_until_stockout'] is not None else float('inf')
        ))
        
        return predictions
    
    def get_low_stock_alerts(self):
        """
        Lấy danh sách cảnh báo hết hàng
        Get low stock alerts
        
        Returns:
            list: Danh sách nguyên liệu sắp hết
        """
        predictions = self.predict_all_ingredients()
        
        # Lọc chỉ lấy HIGH và MEDIUM priority
        alerts = [p for p in predictions if p['priority'] in ['HIGH', 'MEDIUM']]
        
        return alerts
    
    def get_summary(self):
        """
        Lấy tóm tắt tình trạng kho
        Get inventory summary
        
        Returns:
            dict: Tóm tắt
        """
        predictions = self.predict_all_ingredients()
        
        high_priority = len([p for p in predictions if p['priority'] == 'HIGH'])
        medium_priority = len([p for p in predictions if p['priority'] == 'MEDIUM'])
        low_priority = len([p for p in predictions if p['priority'] == 'LOW'])
        
        return {
            'total_ingredients': len(predictions),
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
            'message': f'{high_priority} nguyên liệu cần nhập gấp'
        }
