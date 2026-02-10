from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import json

from .models import Order, OrderItem, Payment
from apps.products.models import Product, Customization
from apps.customers.models import Customer
from apps.staff.models import Staff


@login_required
def create_order(request):
    """
    POS Interface - Tạo đơn hàng
    POS Interface - Create order
    """
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Lấy dữ liệu từ POST
                data = json.loads(request.body)
                
                # Tạo đơn hàng
                order = Order()
                
                # Gán khách hàng nếu có
                customer_id = data.get('customer_id')
                if customer_id:
                    order.customer = Customer.objects.get(id=customer_id)
                
                # Gán nhân viên
                # Giả sử user đã được liên kết với staff
                try:
                    staff = Staff.objects.get(email=request.user.email)
                    order.staff = staff
                except Staff.DoesNotExist:
                    pass
                
                # Tính tổng tiền
                items_data = data.get('items', [])
                total = Decimal('0')
                
                for item_data in items_data:
                    product = Product.objects.get(id=item_data['product_id'])
                    size = item_data['size']
                    quantity = item_data['quantity']
                    
                    # Lấy giá theo size
                    price = product.get_price(size)
                    
                    # Tính giá customizations
                    customizations = item_data.get('customizations', [])
                    custom_price = Decimal('0')
                    for custom_id in customizations:
                        custom = Customization.objects.get(id=custom_id)
                        custom_price += custom.price
                    
                    # Tổng giá item
                    item_total = (price + custom_price) * quantity
                    total += item_total
                
                # Áp dụng giảm giá
                discount = Decimal(data.get('discount', 0))
                final_amount = total - discount
                
                # Lưu đơn hàng
                order.total_amount = total
                order.discount = discount
                order.final_amount = final_amount
                order.status = 'pending'
                order.save()
                
                # Tạo order items
                for item_data in items_data:
                    product = Product.objects.get(id=item_data['product_id'])
                    size = item_data['size']
                    quantity = item_data['quantity']
                    price = product.get_price(size)
                    
                    # Lấy customizations
                    customizations = item_data.get('customizations', [])
                    custom_objs = Customization.objects.filter(id__in=customizations)
                    custom_price = sum(c.price for c in custom_objs)
                    
                    # Lưu customizations dưới dạng JSON
                    custom_json = [{'id': c.id, 'name': c.name, 'price': float(c.price)} 
                                   for c in custom_objs]
                    
                    # Tạo order item
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        size=size,
                        quantity=quantity,
                        price=price,
                        customizations=custom_json,
                        subtotal=(price + custom_price) * quantity
                    )
                
                # Tạo payment
                payment_method = data.get('payment_method', 'cash')
                Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=final_amount
                )
                
                # Đánh dấu hoàn thành
                order.status = 'completed'
                order.save()
                
                return JsonResponse({
                    'success': True,
                    'order_number': order.order_number,
                    'message': 'Đơn hàng đã được tạo thành công'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    # GET request - Hiển thị POS interface
    products = Product.objects.filter(is_available=True).select_related('category')
    customizations = Customization.objects.all()
    
    context = {
        'products': products,
        'customizations': customizations,
    }
    
    return render(request, 'orders/create_order.html', context)


@login_required
def order_list(request):
    """Danh sách đơn hàng"""
    orders = Order.objects.all().select_related('customer', 'staff').order_by('-order_date')
    
    # Lọc theo status nếu có
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """Chi tiết đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_detail.html', context)


@login_required
def search_customer(request):
    """Tìm kiếm khách hàng (AJAX)"""
    phone = request.GET.get('phone', '')
    
    try:
        customer = Customer.objects.get(phone=phone)
        return JsonResponse({
            'found': True,
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'tier': customer.tier,
                'points': customer.points,
                'discount': customer.get_discount_percentage()
            }
        })
    except Customer.DoesNotExist:
        return JsonResponse({
            'found': False,
            'message': 'Không tìm thấy khách hàng'
        })
