import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.orders.models import Order
from decimal import Decimal
from datetime import datetime, timedelta
import pytz

# Tạo datetime hôm nay (3/17) lúc 10:00 sáng Vietnam time
tz = pytz.timezone('Asia/Ho_Chi_Minh')
today = datetime(2026, 3, 17, 10, 0, 0)
now_vn = tz.localize(today)

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
    print(f"✓ Order {i+1}: {order.id} - {order.order_date}")

# Kiểm tra
today_pending = Order.objects.filter(
    order_date__date=datetime(2026, 3, 17).date(),
    status__in=['pending', 'preparing']
)
print(f"\n✓ Total pending orders today: {today_pending.count()}")
for o in today_pending:
    print(f"  - {o.id}: {o.order_date} - status={o.status}")

