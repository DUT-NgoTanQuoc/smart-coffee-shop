import json
import logging
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from apps.core.utils import get_current_staff
from apps.customers.models import Customer
from apps.products.models import Customization, Product

from .models import DiscountCode, Order, OrderItem, Payment

logger = logging.getLogger(__name__)


def _parse_decimal(value, default='0'):
    """Parse Decimal safely from request payload."""
    try:
        return Decimal(str(value))
    except (TypeError, InvalidOperation):
        return Decimal(default)


def _resolve_discount(code_raw, total_amount):
    code_value = (code_raw or '').strip()
    if not code_value:
        return None, Decimal('0')

    discount_code = DiscountCode.objects.filter(code__iexact=code_value).first()
    if not discount_code:
        raise ValueError('Mã giảm giá không tồn tại')

    if not discount_code.is_currently_valid():
        raise ValueError('Mã giảm giá đã hết hạn hoặc đang tạm khóa')

    total = Decimal(str(total_amount or 0))
    if total < discount_code.min_order_amount:
        raise ValueError(
            f'Đơn hàng tối thiểu {discount_code.min_order_amount:,.0f}đ để dùng mã này'
        )

    discount_amount = discount_code.calculate_discount(total)
    if discount_amount <= 0:
        raise ValueError('Mã giảm giá không áp dụng cho đơn hàng hiện tại')

    return discount_code, discount_amount


@login_required
def create_order(request):
    """
    POS interface:
    - GET: render page
    - POST: create pending order
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body or '{}')
        except Exception as exc:
            return JsonResponse(
                {
                    'success': False,
                    'message': f'Dữ liệu đầu vào không hợp lệ: {exc}',
                },
                status=400,
            )

        try:
            with transaction.atomic():
                order = Order()

                customer_id = data.get('customer_id')
                if customer_id:
                    order.customer = Customer.objects.filter(id=customer_id).first()
                    if not order.customer:
                        raise ValueError('Khách hàng không tồn tại')

                try:
                    staff = get_current_staff(request.user)
                    if staff:
                        order.staff = staff
                except Exception:
                    pass

                items_data = data.get('items') or []
                if not isinstance(items_data, list) or not items_data:
                    raise ValueError('Đơn hàng phải có ít nhất 1 sản phẩm')

                total = Decimal('0')
                normalized_items = []

                for item_data in items_data:
                    if not isinstance(item_data, dict):
                        raise ValueError('Dữ liệu sản phẩm không hợp lệ')

                    product_id = item_data.get('product_id', item_data.get('productId'))
                    if not product_id:
                        raise ValueError('Thiếu product_id trong dữ liệu sản phẩm')

                    product = Product.objects.filter(id=product_id, is_available=True).first()
                    if not product:
                        raise ValueError(f'Sản phẩm {product_id} không tồn tại hoặc đang tạm ngưng')

                    size = item_data.get('size') or 'N/A'
                    quantity = int(item_data.get('quantity', item_data.get('qty', 1)))
                    if quantity <= 0:
                        raise ValueError('Số lượng sản phẩm phải lớn hơn 0')

                    price = product.get_price(size)
                    if price is None:
                        raise ValueError(f'Sản phẩm "{product.name}" chưa có giá cho size {size}')

                    customization_ids = item_data.get('customizations') or []
                    if not isinstance(customization_ids, list):
                        raise ValueError('Danh sách tùy chỉnh không hợp lệ')

                    custom_objs = list(Customization.objects.filter(id__in=customization_ids))
                    found_custom_ids = {c.id for c in custom_objs}
                    missing_custom_ids = sorted(set(customization_ids) - found_custom_ids)
                    if missing_custom_ids:
                        raise ValueError(
                            f'Tùy chỉnh không tồn tại: {", ".join(str(cid) for cid in missing_custom_ids)}'
                        )

                    custom_price = sum((c.price for c in custom_objs), Decimal('0'))
                    item_subtotal = (price + custom_price) * quantity
                    total += item_subtotal

                    custom_json = [
                        {'id': c.id, 'name': c.name, 'price': float(c.price)}
                        for c in custom_objs
                    ]

                    normalized_items.append(
                        {
                            'product': product,
                            'size': size,
                            'quantity': quantity,
                            'price': price,
                            'customizations': custom_json,
                            'subtotal': item_subtotal,
                        }
                    )

                discount_code_input = data.get('discount_code')
                discount_code, discount = _resolve_discount(discount_code_input, total)
                if discount > total:
                    raise ValueError('Giảm giá không được lớn hơn tổng tiền')

                final_amount = total - discount

                payment_method = data.get('payment_method', 'cash')
                valid_payment_methods = {code for code, _ in Payment.PAYMENT_METHOD_CHOICES}
                if payment_method not in valid_payment_methods:
                    raise ValueError('Phương thức thanh toán không hợp lệ')

                order.total_amount = total
                order.discount = discount
                order.final_amount = final_amount
                order.status = 'pending'
                order.save()

                for item in normalized_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        size=item['size'],
                        quantity=item['quantity'],
                        price=item['price'],
                        customizations=item['customizations'],
                        subtotal=item['subtotal'],
                    )

                Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=final_amount,
                )

                return JsonResponse(
                    {
                        'success': True,
                        'order_number': order.order_number,
                        'message': 'Đơn hàng đã được tạo thành công',
                        'discount_amount': float(discount),
                        'discount_code': discount_code.code if discount_code else None,
                        'discount_percent': float(discount_code.discount_percent) if discount_code else 0,
                    }
                )

        except ValueError as exc:
            return JsonResponse({'success': False, 'message': str(exc)}, status=400)
        except Exception:
            logger.exception('Unexpected error while creating order')
            return JsonResponse(
                {
                    'success': False,
                    'message': 'Không thể tạo đơn hàng. Vui lòng thử lại.',
                },
                status=500,
            )

    products = Product.objects.filter(is_available=True).select_related('category')
    customizations = Customization.objects.all()

    return render(
        request,
        'orders/create_order.html',
        {
            'products': products,
            'customizations': customizations,
        },
    )


@login_required
def validate_discount_code(request):
    """Validate discount code and return discount amount for current cart total."""
    code_value = (request.GET.get('code', '') or '').strip()
    total_amount = _parse_decimal(request.GET.get('total', 0))

    if not code_value:
        return JsonResponse({'valid': False, 'message': 'Vui lòng nhập mã giảm giá'})
    if total_amount <= 0:
        return JsonResponse({'valid': False, 'message': 'Đơn hàng phải có giá trị lớn hơn 0'})

    try:
        discount_code, discount_amount = _resolve_discount(code_value, total_amount)
    except ValueError as exc:
        return JsonResponse({'valid': False, 'message': str(exc)}, status=400)

    return JsonResponse(
        {
            'valid': True,
            'code': discount_code.code,
            'name': discount_code.name or '',
            'discount_percent': float(discount_code.discount_percent),
            'discount_amount': float(discount_amount),
            'min_order_amount': float(discount_code.min_order_amount),
            'max_discount_amount': float(discount_code.max_discount_amount or 0),
            'message': 'Áp dụng mã giảm giá thành công',
        }
    )


@login_required
def order_list(request):
    """Danh sach don hang."""
    orders = Order.objects.all().select_related('customer', 'staff').order_by('-order_date')

    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Chi tiet don hang."""
    order = get_object_or_404(
        Order.objects.select_related('customer', 'staff').prefetch_related('items__product', 'payments'),
        id=order_id,
    )
    order_items = OrderItem.objects.filter(order_id=order_id).select_related('product').order_by('id')

    return render(
        request,
        'orders/order_detail.html',
        {
            'order': order,
            'order_items': order_items,
        },
    )


@login_required
def search_customer(request):
    """Tim kiem khach hang (AJAX)."""
    phone = (request.GET.get('phone', '') or '').strip()
    if not phone:
        return JsonResponse({'found': False, 'message': 'Vui long nhap so dien thoai'})

    try:
        customer = Customer.objects.get(phone=phone)
        return JsonResponse(
            {
                'found': True,
                'customer': {
                    'id': customer.id,
                    'name': customer.name,
                    'phone': customer.phone,
                    'tier': customer.tier,
                    'points': customer.points,
                    'discount': customer.get_discount_percentage(),
                },
            }
        )
    except Customer.DoesNotExist:
        return JsonResponse({'found': False, 'message': 'Khong tim thay khach hang'})


@login_required
def update_order_status(request, order_id):
    """
    API endpoint - Update order status.
    POST payload: {"status": "pending"|"preparing"|"completed"}
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Don hang khong ton tai'}, status=404)

    is_authorized = False
    if request.user.is_superuser:
        is_authorized = True
    else:
        user_role = getattr(request.user, 'role', None)
        if user_role in {'admin', 'manager', 'barista'}:
            is_authorized = True
        if not is_authorized:
            try:
                staff = get_current_staff(request.user)
                if staff and staff.role in {'manager', 'barista'}:
                    is_authorized = True
            except Exception:
                is_authorized = False

    if not is_authorized:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body or '{}')
    except Exception:
        return JsonResponse({'success': False, 'message': 'Du lieu khong hop le'}, status=400)

    new_status = data.get('status')
    valid_statuses = {code for code, _ in Order.STATUS_CHOICES}
    if new_status not in valid_statuses:
        return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)

    if new_status == order.status:
        return JsonResponse(
            {
                'success': True,
                'message': 'Trang thai khong thay doi',
                'order_id': order.id,
                'status': order.status,
                'status_display': order.get_status_display(),
            }
        )

    allowed_transitions = {
        'pending': {'preparing', 'completed'},
        'preparing': {'completed'},
        'completed': set(),
    }
    if new_status not in allowed_transitions.get(order.status, set()):
        return JsonResponse(
            {
                'success': False,
                'message': f'Khong the chuyen tu "{order.get_status_display()}" sang trang thai nay',
            },
            status=400,
        )

    order.status = new_status
    order.save(update_fields=['status'])

    return JsonResponse(
        {
            'success': True,
            'message': f'Don hang cap nhat thanh: {order.get_status_display()}',
            'order_id': order.id,
            'status': order.status,
            'status_display': order.get_status_display(),
        }
    )
