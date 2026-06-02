from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from .models import Product, Category, Recipe, Customization
from .forms import ProductForm
from apps.orders.models import DiscountCode
from decimal import Decimal, InvalidOperation


@login_required
def product_list(request):
    """Danh sách sản phẩm"""
    products = Product.objects.all().select_related('category')
    
    # Lọc theo category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()
    discount_codes = DiscountCode.objects.all().order_by('-created_at')
    discount_count = discount_codes.count()
    
    context = {
        'products': products,
        'categories': categories,
        'discount_codes': discount_codes,
        'discount_count': discount_count,
    }
    
    return render(request, 'products/product_list.html', context)


@login_required
def discount_code_create(request):
    """Create discount code from the dedicated discount manager page."""
    if request.method != 'POST':
        return redirect('discount_code_manager')

    code = (request.POST.get('code') or '').strip().upper()
    name = (request.POST.get('name') or '').strip()
    description = (request.POST.get('description') or '').strip()
    discount_percent_raw = (request.POST.get('discount_percent') or '').strip()
    min_order_amount_raw = (request.POST.get('min_order_amount') or '0').strip()
    max_discount_amount_raw = (request.POST.get('max_discount_amount') or '').strip()
    valid_from = (request.POST.get('valid_from') or '').strip()
    valid_to = (request.POST.get('valid_to') or '').strip()
    is_active = request.POST.get('is_active') == 'on'

    if not code:
        messages.error(request, 'Vui lòng nhập mã giảm giá.')
        return redirect('product_list')

    try:
        discount_percent = Decimal(discount_percent_raw)
        min_order_amount = Decimal(min_order_amount_raw or '0')
        max_discount_amount = Decimal(max_discount_amount_raw) if max_discount_amount_raw else None
    except (InvalidOperation, TypeError):
        messages.error(request, 'Giá trị phần trăm hoặc số tiền không hợp lệ.')
        return redirect('product_list')

    discount_code, created = DiscountCode.objects.get_or_create(
        code=code,
        defaults={
            'name': name,
            'description': description or None,
            'discount_percent': discount_percent,
            'min_order_amount': min_order_amount,
            'max_discount_amount': max_discount_amount,
            'is_active': is_active,
        },
    )

    discount_code.name = name
    discount_code.description = description or None
    discount_code.discount_percent = discount_percent
    discount_code.min_order_amount = min_order_amount
    discount_code.max_discount_amount = max_discount_amount
    discount_code.is_active = is_active

    if valid_from:
        parsed = parse_datetime(valid_from)
        discount_code.valid_from = parsed
    else:
        discount_code.valid_from = None

    if valid_to:
        parsed = parse_datetime(valid_to)
        discount_code.valid_to = parsed
    else:
        discount_code.valid_to = None

    try:
        discount_code.full_clean()
        discount_code.save()
    except Exception as exc:
        messages.error(request, f'Không thể lưu mã giảm giá: {exc}')
        return redirect('product_list')

    messages.success(request, f'Đã {"tạo" if created else "cập nhật"} mã giảm giá {discount_code.code}.')
    return redirect('discount_code_manager')


@login_required
def discount_code_manager(request):
    """Dedicated discount code management page."""
    discount_codes = DiscountCode.objects.all().order_by('-created_at')
    context = {
        'discount_codes': discount_codes,
    }
    return render(request, 'products/discount_code_manager.html', context)


@login_required
def discount_code_update(request, code_id):
    """Update existing discount code."""
    discount_code = get_object_or_404(DiscountCode, id=code_id)
    if request.method != 'POST':
        return redirect('discount_code_manager')

    code = (request.POST.get('code') or '').strip().upper()
    name = (request.POST.get('name') or '').strip()
    description = (request.POST.get('description') or '').strip()
    discount_percent_raw = (request.POST.get('discount_percent') or '').strip()
    min_order_amount_raw = (request.POST.get('min_order_amount') or '0').strip()
    max_discount_amount_raw = (request.POST.get('max_discount_amount') or '').strip()
    valid_from = (request.POST.get('valid_from') or '').strip()
    valid_to = (request.POST.get('valid_to') or '').strip()
    is_active = request.POST.get('is_active') == 'on'

    try:
        discount_percent = Decimal(discount_percent_raw)
        min_order_amount = Decimal(min_order_amount_raw or '0')
        max_discount_amount = Decimal(max_discount_amount_raw) if max_discount_amount_raw else None
    except (InvalidOperation, TypeError):
        messages.error(request, 'Giá trị phần trăm hoặc số tiền không hợp lệ.')
        return redirect('discount_code_manager')

    discount_code.code = code or discount_code.code
    discount_code.name = name
    discount_code.description = description or None
    discount_code.discount_percent = discount_percent
    discount_code.min_order_amount = min_order_amount
    discount_code.max_discount_amount = max_discount_amount
    discount_code.is_active = is_active

    parsed = parse_datetime(valid_from) if valid_from else None
    discount_code.valid_from = parsed
    parsed = parse_datetime(valid_to) if valid_to else None
    discount_code.valid_to = parsed

    try:
        discount_code.full_clean()
        discount_code.save()
        messages.success(request, f'Đã cập nhật mã giảm giá {discount_code.code}.')
    except Exception as exc:
        messages.error(request, f'Không thể cập nhật mã giảm giá: {exc}')

    return redirect('discount_code_manager')


@login_required
def discount_code_delete(request, code_id):
    """Delete a discount code."""
    discount_code = get_object_or_404(DiscountCode, id=code_id)
    if request.method == 'POST':
        discount_code.delete()
        messages.success(request, f'Đã xóa mã giảm giá {discount_code.code}.')
    return redirect('discount_code_manager')


@login_required
def product_detail(request, product_id):
    """Chi tiết sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    recipes = Recipe.objects.filter(product=product).select_related('ingredient')
    
    context = {
        'product': product,
        'recipes': recipes,
    }
    
    return render(request, 'products/product_detail.html', context)


@login_required
def product_create(request):
    """Tạo sản phẩm mới"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Sản phẩm đã được tạo thành công!')
            return redirect('product_detail', product_id=product.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'product': None,  # Truyền product=None để template biết đây là tạo mới
    }
    
    return render(request, 'products/product_form.html', context)


@login_required
def product_update(request, product_id):
    """Cập nhật sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được cập nhật!')
            return redirect('product_detail', product_id=product.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
    }
    
    return render(request, 'products/product_form.html', context)


@login_required
def product_delete(request, product_id):
    """Xóa sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Sản phẩm đã được xóa!')
        return redirect('product_list')
    
    context = {
        'product': product,
    }
    
    return render(request, 'products/product_confirm_delete.html', context)
