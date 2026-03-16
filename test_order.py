import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.orders.models import Order
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta
import pytz

# Tạo datetime hôm nay (3/17) lúc 10:00 sáng Vietnam time
tz = pytz.timezone('Asia/Ho_Chi_Minh')
now_vn = datetime.now(tz).replace(hour=10, minute=0, second=0, microsecond=0)

print(f"Creating orders with date: {now_vn}")

# Tạo 5 đơn test hôm nay
for i in range(5):
    order = Order.objects.create(
        total_amount=Decimal('50000'),
        discount=Decimal('0'),
        final_amount=Decimal('50000'),
        status='pending',
        order_date=now_vn + timedelta(minutes=i*5)
    )
    print(f"✓ Tạo đơn {i+1}: {order.id} - {order.order_date}")

# Kiểm tra
today_pending = Order.objects.filter(order_date__date=timezone.now().date()).exclude(status='completed')
print(f"\n✓ Tổng đơn pending hôm nay: {today_pending.count()}")
for o in today_pending[:5]:
    print(f"  - {o.id}: {o.order_date}")

