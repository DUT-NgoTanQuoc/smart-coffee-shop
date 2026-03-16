import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseForbidden

from apps.core.models import Account
from .forms import IngredientForm, IngredientRestockForm
from .models import Ingredient


# Views có thể được truy cập bởi admin hoặc barista
def ingredient_access_required(view_func):
    """Decorator cho phép admin hoặc barista truy cập"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Cho phép admin (Django superuser)
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Cho phép barista (role_id = 3)
        try:
            account = Account.objects.get(username=request.user.username)
            if account.role_id == 3:  # barista
                return view_func(request, *args, **kwargs)
        except Account.DoesNotExist:
            pass
        
        return HttpResponseForbidden('Bạn không có quyền truy cập trang này.')
    return wrapper


@login_required
@ingredient_access_required
def ingredient_list(request):
    """Danh sách nguyên liệu"""
    ingredients = Ingredient.objects.all().order_by('name')

    # Lọc nguyên liệu sắp hết
    low_stock_only = request.GET.get('low_stock')
    if low_stock_only:
        ingredients = ingredients.filter(quantity__lte=F('min_quantity'))

    context = {
        'ingredients': ingredients,
        'low_stock_only': bool(low_stock_only),
    }
    
    return render(request, 'ingredients/ingredient_list.html', context)


@login_required
@ingredient_access_required
def ingredient_create(request):
    """Tạo nguyên liệu mới"""
    form = IngredientForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            ingredient = form.save()
            messages.success(request, 'Nguyên liệu đã được tạo thành công!')
            return redirect('ingredient_list')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin vừa nhập.')

    return render(request, 'ingredients/ingredient_form.html', {'form': form})


@login_required
@ingredient_access_required
def ingredient_update(request, ingredient_id):
    """Cập nhật nguyên liệu"""
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)

    form = IngredientForm(request.POST or None, instance=ingredient)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Nguyên liệu đã được cập nhật!')
            return redirect('ingredient_list')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin vừa nhập.')

    context = {
        'ingredient': ingredient,
        'form': form,
    }

    return render(request, 'ingredients/ingredient_form.html', context)


@login_required
@ingredient_access_required
def ingredient_restock(request, ingredient_id):
    """Nhập thêm nguyên liệu"""
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)

    form = IngredientRestockForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            quantity_to_add = form.cleaned_data['quantity']
            before_quantity = ingredient.quantity
            before_restock_date = ingredient.last_restock_date

            ingredient.add_stock(quantity_to_add)

            ingredient.last_restock_date = timezone.now().date()
            ingredient.save()

            total_value = quantity_to_add * ingredient.price_per_unit
            _log_restock_action(
                request,
                ingredient,
                quantity_to_add,
                before_quantity,
                before_restock_date,
                total_value,
            )

            messages.success(request, f'Đã nhập thêm {quantity_to_add} {ingredient.unit}')
            return redirect('ingredient_list')
        messages.error(request, 'Vui lòng nhập số lượng hợp lệ (> 0).')

    context = {
        'ingredient': ingredient,
        'form': form,
    }

    return render(request, 'ingredients/ingredient_restock.html', context)


def _log_restock_action(
    request,
    ingredient: Ingredient,
    added_qty: Decimal,
    before_qty: Decimal,
    before_restock_date,
    total_value: Decimal,
):
    """Ghi log nhập kho vào bảng audit_logs (có sẵn trong schema)."""
    try:
        new_quantity = ingredient.quantity
        data_old = {
            'quantity': str(before_qty),
            'last_restock_date': before_restock_date.isoformat() if before_restock_date else None,
        }
        data_new = {
            'added_quantity': str(added_qty),
            'new_quantity': str(new_quantity),
            'total_value': str(total_value),
        }

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO audit_logs (account_id, action, module, target_id, old_data, new_data, ip_address)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s)
                """,
                [
                    request.user.id if request.user.is_authenticated else None,
                    'ingredient.restock',
                    'ingredient',
                    ingredient.id,
                    json.dumps(data_old),
                    json.dumps(data_new),
                    request.META.get('REMOTE_ADDR'),
                ],
            )
    except Exception:
        # Không chặn luồng chính nếu việc log thất bại
        return
