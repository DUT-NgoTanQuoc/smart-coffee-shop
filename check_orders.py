import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.orders.models import Order
from datetime import datetime

today = datetime(2026, 3, 17).date()
all_today = Order.objects.filter(order_date__date=today)
print(f'All today: {all_today.count()}')
for o in all_today[:10]:
    print(f'  - {o.id}: status={o.status}, date={o.order_date}')

pending_only = Order.objects.filter(order_date__date=today, status='pending')
print(f'\nPending only: {pending_only.count()}')
