"""
Seed a large, realistic-looking dataset for demo/testing.

Usage:
    python scripts/seed_realistic_data.py
"""

import os
import random
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta, time
from decimal import Decimal
from pathlib import Path

import django
from django.db import transaction
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
os.chdir(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analytics.models import DailyStat  # noqa: E402
from apps.customers.models import Customer  # noqa: E402
from apps.orders.models import DiscountCode, Order, OrderItem, Payment  # noqa: E402
from apps.products.models import Product  # noqa: E402
from apps.staff.models import Staff, WorkLog  # noqa: E402


LAST_NAMES = [
    'Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ',
    'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý',
]
MIDDLE_NAMES = [
    'Văn', 'Thị', 'Quốc', 'Minh', 'Ngọc', 'Thanh', 'Đức', 'Hữu',
    'Gia', 'Xuân', 'Khánh', 'Hoài', 'Bảo', 'Anh', 'Trọng', 'Kim',
]
FIRST_NAMES = [
    'Tiến', 'Hùng', 'Long', 'Khang', 'Nam', 'Duy', 'Hải', 'Linh', 'Trang',
    'Hà', 'My', 'Nhi', 'Phương', 'Quỳnh', 'Thảo', 'Hương', 'Tuấn', 'Phúc',
    'Tâm', 'Thu', 'Lan', 'Giang', 'Nhung', 'Khôi', 'Đạt', 'Sơn', 'Thành',
]
DOMAINS = [
    'gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com', 'hotmail.com',
    'proton.me', 'mail.com',
]
PHONE_PREFIXES = ['03', '05', '07', '08', '09']


def slugify_name(name):
    name = name.replace('Đ', 'D').replace('đ', 'd')
    normalized = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    return ''.join(ch for ch in normalized.lower() if ch.isalnum())


def random_name():
    return f"{random.choice(LAST_NAMES)} {random.choice(MIDDLE_NAMES)} {random.choice(FIRST_NAMES)}"


def random_phone(existing):
    while True:
        phone = random.choice(PHONE_PREFIXES) + ''.join(random.choices('0123456789', k=8))
        if phone not in existing:
            existing.add(phone)
            return phone


def random_email(name, existing):
    base = slugify_name(name)
    while True:
        suffix = ''.join(random.choices('0123456789', k=3))
        email = f'{base}{suffix}@{random.choice(DOMAINS)}'
        if email not in existing:
            existing.add(email)
            return email


def tier_by_points(points):
    if points >= 5000:
        return 'Kim cương'
    if points >= 2000:
        return 'Vàng'
    if points >= 500:
        return 'Bạc'
    return 'Đồng'


def ensure_discount_codes():
    now = timezone.now()
    presets = [
        ('KHAITRUONG10', 'Khuyến mãi khai trương', Decimal('10.00'), Decimal('50000'), Decimal('50000')),
        ('COFFEE15', 'Ưu đãi Coffee', Decimal('15.00'), Decimal('100000'), Decimal('80000')),
        ('SANGSOM5', 'Ưu đãi buổi sáng', Decimal('5.00'), Decimal('30000'), Decimal('30000')),
        ('THANHVIEN20', 'Ưu đãi thành viên', Decimal('20.00'), Decimal('150000'), Decimal('120000')),
        ('WEEKEND12', 'Cuối tuần vui vẻ', Decimal('12.00'), Decimal('80000'), Decimal('60000')),
    ]

    for code, name, percent, min_order, cap in presets:
        DiscountCode.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'discount_percent': percent,
                'min_order_amount': min_order,
                'max_discount_amount': cap,
                'is_active': True,
                'valid_from': now - timedelta(days=365),
                'valid_to': now + timedelta(days=365),
            },
        )


def seed_customers(target_add=500):
    existing_phones = set(Customer.objects.values_list('phone', flat=True))
    existing_emails = set(
        email for email in Customer.objects.values_list('email', flat=True) if email
    )

    rows = []
    for _ in range(target_add):
        name = random_name()
        phone = random_phone(existing_phones)
        email = random_email(name, existing_emails)
        points = random.randint(0, 9000)
        rows.append(
            Customer(
                name=name,
                phone=phone,
                email=email,
                points=points,
                tier=tier_by_points(points),
            )
        )
    Customer.objects.bulk_create(rows, batch_size=200)
    return len(rows)


def seed_staff(target_add=80):
    existing_phones = set(Staff.objects.values_list('phone', flat=True))
    existing_emails = set(email for email in Staff.objects.values_list('email', flat=True) if email)

    role_weights = [('cashier', 35), ('barista', 40), ('parttime', 20), ('manager', 5)]
    role_pool = []
    for role, weight in role_weights:
        role_pool.extend([role] * weight)

    rows = []
    for _ in range(target_add):
        name = random_name()
        phone = random_phone(existing_phones)
        email = random_email(name, existing_emails)
        role = random.choice(role_pool)
        if role == 'manager':
            salary = random.randint(12000000, 20000000)
        elif role == 'cashier':
            salary = random.randint(7000000, 11000000)
        elif role == 'barista':
            salary = random.randint(6500000, 10000000)
        else:
            salary = random.randint(4500000, 8000000)

        hire_days_ago = random.randint(30, 1400)
        hire_date = timezone.localdate() - timedelta(days=hire_days_ago)
        rows.append(
            Staff(
                name=name,
                phone=phone,
                email=email,
                role=role,
                salary=salary,
                hire_date=hire_date,
                is_active=random.random() > 0.08,
            )
        )

    Staff.objects.bulk_create(rows, batch_size=100)
    return len(rows)


def _extract_existing_sequences():
    seq_map = defaultdict(int)
    for number in Order.objects.values_list('order_number', flat=True):
        if not number or not number.startswith('ORD') or len(number) < 12:
            continue
        date_key = number[3:11]
        seq_part = number[11:]
        if seq_part.isdigit():
            seq_map[date_key] = max(seq_map[date_key], int(seq_part))
    return seq_map


def _available_sizes(product):
    sizes = []
    if product.price_small:
        sizes.append(('S', Decimal(product.price_small)))
    if product.price_medium:
        sizes.append(('M', Decimal(product.price_medium)))
    if product.price_large:
        sizes.append(('L', Decimal(product.price_large)))
    if not sizes:
        fallback = product.get_price('N/A')
        if fallback:
            sizes.append(('N/A', Decimal(fallback)))
    return sizes


def seed_orders(target_add=3500):
    products = list(Product.objects.filter(is_available=True))
    if not products:
        return 0

    customers = list(Customer.objects.all())
    staff_pool = list(Staff.objects.filter(is_active=True))
    if not staff_pool:
        staff_pool = list(Staff.objects.all())

    product_sizes = {p.id: _available_sizes(p) for p in products}
    product_sizes = {k: v for k, v in product_sizes.items() if v}
    products = [p for p in products if p.id in product_sizes]
    if not products:
        return 0

    seq_map = _extract_existing_sequences()
    used_order_numbers = set(Order.objects.values_list('order_number', flat=True))

    order_rows = []
    item_payloads = []
    payment_rows = []
    points_by_customer = defaultdict(int)

    status_pool = (
        ['completed'] * 82 +
        ['pending'] * 10 +
        ['preparing'] * 8
    )

    now = timezone.now()
    for _ in range(target_add):
        days_back = random.randint(0, 210)
        random_date = (timezone.localdate() - timedelta(days=days_back))
        random_time = time(
            hour=random.randint(6, 22),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
        )
        order_dt = timezone.make_aware(datetime.combine(random_date, random_time))
        date_key = order_dt.strftime('%Y%m%d')
        seq = seq_map[date_key] + 1
        order_no = f'ORD{date_key}{seq:03d}'
        while order_no in used_order_numbers:
            seq += 1
            order_no = f'ORD{date_key}{seq:03d}'
        seq_map[date_key] = seq
        used_order_numbers.add(order_no)

        customer = random.choice(customers) if customers and random.random() < 0.82 else None
        staff = random.choice(staff_pool) if staff_pool and random.random() < 0.95 else None

        line_count = random.randint(1, 5)
        order_items = []
        total = Decimal('0')
        for _line in range(line_count):
            product = random.choice(products)
            size, price = random.choice(product_sizes[product.id])
            quantity = random.randint(1, 3)
            subtotal = (price * quantity).quantize(Decimal('0.01'))
            total += subtotal
            order_items.append(
                {
                    'product': product,
                    'size': size,
                    'quantity': quantity,
                    'price': price,
                    'subtotal': subtotal,
                }
            )

        discount = Decimal('0')
        if random.random() < 0.35:
            percent = Decimal(str(random.choice([5, 8, 10, 12, 15, 20])))
            discount = (total * percent / Decimal('100')).quantize(Decimal('0.01'))
            discount_cap = Decimal(str(random.choice([30000, 50000, 80000, 120000])))
            discount = min(discount, discount_cap)
            discount = min(discount, total)

        final_amount = (total - discount).quantize(Decimal('0.01'))
        status = random.choice(status_pool)
        points_earned = int(final_amount / Decimal('10000')) if status == 'completed' and customer else 0

        order_rows.append(
            Order(
                order_number=order_no,
                customer=customer,
                staff=staff,
                total_amount=total,
                discount=discount,
                final_amount=final_amount,
                status=status,
                order_date=order_dt,
                points_earned=points_earned,
                points_used=0,
            )
        )
        item_payloads.append(order_items)
        payment_rows.append(
            {
                'payment_method': random.choice(['cash', 'card', 'momo']),
                'amount': final_amount,
                'payment_date': order_dt + timedelta(minutes=random.randint(1, 25)),
            }
        )

        if customer and status == 'completed':
            points_by_customer[customer.id] += points_earned

    with transaction.atomic():
        created_orders = Order.objects.bulk_create(order_rows, batch_size=400)

        order_item_rows = []
        payment_model_rows = []
        for idx, order in enumerate(created_orders):
            for payload in item_payloads[idx]:
                order_item_rows.append(
                    OrderItem(
                        order=order,
                        product=payload['product'],
                        size=payload['size'],
                        quantity=payload['quantity'],
                        price=payload['price'],
                        customizations=[],
                        subtotal=payload['subtotal'],
                    )
                )

            payment_data = payment_rows[idx]
            payment_model_rows.append(
                Payment(
                    order=order,
                    payment_method=payment_data['payment_method'],
                    amount=payment_data['amount'],
                    payment_date=payment_data['payment_date'],
                )
            )

        OrderItem.objects.bulk_create(order_item_rows, batch_size=1000)
        Payment.objects.bulk_create(payment_model_rows, batch_size=1000)

        if points_by_customer:
            customers_to_update = list(Customer.objects.filter(id__in=points_by_customer.keys()))
            for customer in customers_to_update:
                customer.points += points_by_customer[customer.id]
                customer.tier = tier_by_points(customer.points)
            Customer.objects.bulk_update(customers_to_update, ['points', 'tier'], batch_size=500)

    return len(created_orders)


def rebuild_daily_stats():
    aggregates = (
        Order.objects.filter(status='completed')
        .annotate(day=TruncDate('order_date'))
        .values('day')
        .annotate(
            total_revenue=Sum('final_amount'),
            total_orders=Count('id'),
            total_customers=Count('customer', distinct=True),
        )
        .order_by('day')
    )

    rows = []
    for item in aggregates:
        rows.append(
            DailyStat(
                stat_date=item['day'],
                total_revenue=item['total_revenue'] or 0,
                total_orders=item['total_orders'] or 0,
                total_customers=item['total_customers'] or 0,
            )
        )

    with transaction.atomic():
        DailyStat.objects.all().delete()
        DailyStat.objects.bulk_create(rows, batch_size=500)

    return len(rows)


def seed_worklogs(days=60):
    staff_members = list(Staff.objects.filter(is_active=True))
    if not staff_members:
        return 0

    created = 0
    for day_offset in range(days):
        work_date = timezone.localdate() - timedelta(days=day_offset)
        random.shuffle(staff_members)
        todays_staff = staff_members[: random.randint(max(8, len(staff_members) // 4), max(12, len(staff_members) // 2))]
        rows = []
        for staff in todays_staff:
            if WorkLog.objects.filter(staff=staff, work_date=work_date).exists():
                continue
            check_in_hour = random.randint(6, 10)
            check_in_min = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
            duration = random.uniform(6.0, 10.5)
            check_in = time(check_in_hour, check_in_min)
            out_dt = datetime.combine(work_date, check_in) + timedelta(hours=duration)
            check_out = out_dt.time()
            rows.append(
                WorkLog(
                    staff=staff,
                    work_date=work_date,
                    check_in=check_in,
                    check_out=check_out,
                    hours_worked=round(duration, 2),
                )
            )
        if rows:
            WorkLog.objects.bulk_create(rows, batch_size=300)
            created += len(rows)
    return created


def main():
    random.seed(20260502)
    print('Seeding realistic demo data...')
    ensure_discount_codes()

    added_customers = seed_customers(target_add=500)
    print(f'  + Customers: {added_customers}')

    added_staff = seed_staff(target_add=80)
    print(f'  + Staff: {added_staff}')

    added_orders = seed_orders(target_add=3500)
    print(f'  + Orders: {added_orders}')

    rebuilt_stats = rebuild_daily_stats()
    print(f'  + Daily stats rows rebuilt: {rebuilt_stats}')

    added_logs = seed_worklogs(days=60)
    print(f'  + Work logs: {added_logs}')

    print('Done.')


if __name__ == '__main__':
    main()
