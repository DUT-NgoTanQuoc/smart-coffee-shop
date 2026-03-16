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
from apps.core.utils import get_current_staff


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
                print(f"[CREATE_ORDER] POST data: {data}")
                
                # Tạo đơn hàng
                order = Order()
                
                # Gán khách hàng nếu có
                customer_id = data.get('customer_id')
                if customer_id:
                    order.customer = Customer.objects.get(id=customer_id)
                
                # Gán nhân viên (dựa trên accounts table hoặc email/phone)
                try:
                    staff = get_current_staff(request.user)
                    if staff:
                        order.staff = staff
                except Exception:
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
                print(f"[CREATE_ORDER] Order created: {order.id}, items: {len(items_data)}")
                
                # Tạo order items
                for item_data in items_data:
                    print(f"[CREATE_ORDER] Processing item: {item_data}")
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
                    print(f"[CREATE_ORDER] OrderItem created: {product.name} x{quantity}")
                
                # Tạo payment
                payment_method = data.get('payment_method', 'cash')
                Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=final_amount
                )
                
                # Status vẫn là 'pending' để barista xử lý (KHÔNG set thành 'completed')
                # order.status = 'completed'
                # order.save()
                
                return JsonResponse({
                    'success': True,
                    'order_number': order.order_number,
                    'message': 'Đơn hàng đã được tạo thành công'
                })
                
        except Exception as e:
            import traceback
            print(f"[CREATE_ORDER] ERROR: {str(e)}")
            print(traceback.format_exc())
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


@login_required
def update_order_status(request, order_id):
    """
    API endpoint - Update order status
    POST: {status: 'pending' | 'preparing' | 'completed'}
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Check permission - only barista/admin can update
        if not request.user.is_superuser:
            try:
                staff = get_current_staff(request.user)
                if not staff or staff.role not in ['barista', 'admin']:
                    return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
            except:
                return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
        
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return JsonResponse({'success': False, 'message': 'Invalid status'})
        
        order.status = new_status
        if new_status == 'completed':
            order.completed_at = timezone.now()
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Đơn hàng cập nhật thành: {order.get_status_display()}',
            'order_id': order.id,
            'status': order.status,
            'status_display': order.get_status_display(),
        })
    
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Đơn hàng không tồn tại'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
