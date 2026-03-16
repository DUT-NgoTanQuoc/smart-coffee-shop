#!/usr/bin/env python
import os
import django
from datetime import date, datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.products.models import Product, Category, Recipe
from apps.ingredients.models import Ingredient
from apps.customers.models import Customer
from apps.orders.models import Order, OrderItem
from apps.staff.models import Staff

# Xóa dữ liệu cũ (optional - comment out để giữ dữ liệu)
# Category.objects.all().delete()
# Product.objects.all().delete()
# Ingredient.objects.all().delete()
# Customer.objects.all().delete()
# Order.objects.all().delete()
# Staff.objects.all().delete()

print("Creating sample data...\n")

# 1. Tạo Category
categories = []
cat_names = ['Cà phê', 'Trà', 'Nước ngọt', 'Bánh']
for name in cat_names:
    cat, created = Category.objects.get_or_create(
        name=name,
        defaults={'description': f'Danh mục {name}'}
    )
    categories.append(cat)
    print(f"✅ Category: {name}")

# 2. Tạo Ingredients
ingredients = []
ingredient_data = [
    {'name': 'Cà phê hạt', 'unit': 'g', 'quantity': 5000},
    {'name': 'Sữa tươi', 'unit': 'L', 'quantity': 20},
    {'name': 'Đường', 'unit': 'kg', 'quantity': 10},
    {'name': 'Kem', 'unit': 'L', 'quantity': 5},
    {'name': 'Trà đen', 'unit': 'g', 'quantity': 2000},
    {'name': 'Nước chanh', 'unit': 'L', 'quantity': 10},
]

for data in ingredient_data:
    ing, created = Ingredient.objects.get_or_create(
        name=data['name'],
        defaults={
            'unit': data['unit'],
            'quantity': data['quantity'],
            'reorder_level': 500
        }
    )
    ingredients.append(ing)
    print(f"✅ Ingredient: {data['name']}")

# 3. Tạo Products
products_data = [
    {'name': 'Espresso', 'category': categories[0], 'price': 25000, 'description': 'Cà phê đen đậm đà'},
    {'name': 'Cappuccino', 'category': categories[0], 'price': 35000, 'description': 'Cà phê với sữa'},
    {'name': 'Latte', 'category': categories[0], 'price': 40000, 'description': 'Cà phê sữa ít đắng'},
    {'name': 'Americano', 'category': categories[0], 'price': 30000, 'description': 'Cà phê pha nước'},
    {'name': 'Trà đen', 'category': categories[1], 'price': 20000, 'description': 'Trà đen nguyên chất'},
    {'name': 'Trà chanh', 'category': categories[1], 'price': 25000, 'description': 'Trà đen với chanh'},
    {'name': 'Coke', 'category': categories[2], 'price': 15000, 'description': 'Nước ngọt'},
    {'name': 'Bánh Croissant', 'category': categories[3], 'price': 30000, 'description': 'Bánh nước ngoài'},
]

products = []
for data in products_data:
    product, created = Product.objects.get_or_create(
        name=data['name'],
        defaults={
            'category': data['category'],
            'price': data['price'],
            'description': data['description'],
            'is_available': True
        }
    )
    products.append(product)
    print(f"✅ Product: {data['name']}")

# 4. Tạo Recipes cho coffee
if len(products) >= 4 and len(ingredients) >= 4:
    # Espresso recipe
    Recipe.objects.get_or_create(
        product=products[0],
        defaults={
            'ingredients': f"{ingredients[0].name}: 15g\n{ingredients[2].name}: 5g",
            'instructions': '1. Xay cà phê\n2. Pha espresso'
        }
    )
    # Cappuccino recipe
    Recipe.objects.get_or_create(
        product=products[1],
        defaults={
            'ingredients': f"{ingredients[0].name}: 15g\n{ingredients[1].name}: 150ml\n{ingredients[3].name}: 50ml",
            'instructions': '1. Pha espresso\n2. Đánh sữa\n3. Trộn lại'
        }
    )
    print(f"✅ Recipes created")

# 5. Tạo Customers
customers_data = [
    {'name': 'Nguyễn Văn A', 'phone': '0901234567', 'email': 'a@example.com'},
    {'name': 'Trần Thị B', 'phone': '0912345678', 'email': 'b@example.com'},
    {'name': 'Lê Văn C', 'phone': '0923456789', 'email': 'c@example.com'},
]

customers = []
for data in customers_data:
    customer, created = Customer.objects.get_or_create(
        phone=data['phone'],
        defaults={
            'name': data['name'],
            'email': data['email'],
            'total_points': 0
        }
    )
    customers.append(customer)
    print(f"✅ Customer: {data['name']}")

# 6. Tạo Orders
if customers:
    orders_data = [
        {'customer': customers[0], 'status': 'completed', 'total': 75000},
        {'customer': customers[1], 'status': 'completed', 'total': 40000},
        {'customer': customers[0], 'status': 'pending', 'total': 35000},
    ]
    
    for idx, data in enumerate(orders_data):
        order, created = Order.objects.get_or_create(
            id=100 + idx if not Order.objects.filter(id=100+idx).exists() else None,
            defaults={
                'customer': data['customer'],
                'order_status': data['status'],
                'total': data['total'],
                'created_at': datetime.now() - timedelta(hours=idx*2)
            }
        )
        
        # Add order items
        if created and products:
            OrderItem.objects.create(
                order=order,
                product=products[idx % len(products)],
                quantity=2,
                size='L'
            )
        
        print(f"✅ Order #{order.id}: {data['status']}")

print("\n✅ Sample data created successfully!")
