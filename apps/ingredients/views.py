import json
from calendar import monthrange
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.analytics.ml_models.stock_predictor import StockPredictor
from apps.core.models import Account
from apps.core.utils import get_current_staff

from .forms import IngredientForm, IngredientRestockForm
from .models import Ingredient


def ingredient_access_required(view_func):
    """Decorator cho phép admin hoặc barista truy cập."""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        user_role = getattr(request.user, 'role', None)
        if user_role in {'admin', 'manager', 'barista'}:
            return view_func(request, *args, **kwargs)

        try:
            account = Account.objects.filter(username=request.user.username).only('role_id').first()
            if account and account.role_id == 3:
                return view_func(request, *args, **kwargs)
        except Exception:
            pass

        try:
            staff = get_current_staff(request.user)
            if staff and staff.role in {'manager', 'barista'}:
                return view_func(request, *args, **kwargs)
        except Exception:
            pass

        return HttpResponseForbidden('Bạn không có quyền truy cập trang này.')

    return wrapper


def _build_prediction_context():
    stock_predictor = StockPredictor()
    predictions = stock_predictor.predict_all_ingredients()
    prediction_summary = stock_predictor.get_summary()

    today = timezone.now().date()
    next_month_year = today.year + (1 if today.month == 12 else 0)
    next_month = 1 if today.month == 12 else today.month + 1
    next_month_days = monthrange(next_month_year, next_month)[1]

    monthly_import_suggestions = []
    for pred in predictions:
        monthly_need = round(pred['daily_consumption'] * next_month_days, 2)
        suggested_import = max(0, round(monthly_need - pred['current_stock'], 2))
        estimated_cost = round(suggested_import * float(pred['ingredient'].price_per_unit), 2)

        if suggested_import > 0:
            monthly_import_suggestions.append(
                {
                    'ingredient': pred['ingredient'],
                    'priority': pred['priority'],
                    'current_stock': pred['current_stock'],
                    'daily_consumption': pred['daily_consumption'],
                    'monthly_need': monthly_need,
                    'suggested_import': suggested_import,
                    'unit': pred['unit'],
                    'estimated_cost': estimated_cost,
                }
            )

    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    monthly_import_suggestions.sort(
        key=lambda row: (priority_order.get(row['priority'], 3), -row['suggested_import'])
    )

    import_chart = {
        'labels': [item['ingredient'].name for item in monthly_import_suggestions[:10]],
        'monthly_need': [item['monthly_need'] for item in monthly_import_suggestions[:10]],
        'suggested_import': [item['suggested_import'] for item in monthly_import_suggestions[:10]],
    }

    return {
        'prediction_summary': prediction_summary,
        'predictions': predictions[:30],
        'monthly_import_suggestions': monthly_import_suggestions[:30],
        'next_month_label': f'{next_month:02d}/{next_month_year}',
        'next_month_days': next_month_days,
        'import_chart_json': json.dumps(import_chart),
    }


@login_required
@ingredient_access_required
def ingredient_list(request):
    """Danh sách nguyên liệu (bản gọn)."""
    ingredients = Ingredient.objects.all().order_by('name')

    low_stock_only = request.GET.get('low_stock')
    if low_stock_only:
        ingredients = ingredients.filter(quantity__lte=F('min_quantity'))

    low_stock_count = Ingredient.objects.filter(quantity__lte=F('min_quantity')).count()
    context = {
        'ingredients': ingredients,
        'low_stock_only': bool(low_stock_only),
        'low_stock_count': low_stock_count,
    }
    return render(request, 'ingredients/ingredient_list.html', context)


@login_required
@ingredient_access_required
def ingredient_forecast(request):
    """Trang gợi ý nhập và dự báo tồn kho."""
    context = _build_prediction_context()
    return render(request, 'ingredients/ingredient_forecast.html', context)


@login_required
@ingredient_access_required
def ingredient_create(request):
    """Tạo nguyên liệu mới."""
    form = IngredientForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Nguyên liệu đã được tạo thành công!')
            return redirect('ingredient_list')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin vừa nhập.')

    return render(request, 'ingredients/ingredient_form.html', {'form': form})


@login_required
@ingredient_access_required
def ingredient_update(request, ingredient_id):
    """Cập nhật nguyên liệu."""
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    form = IngredientForm(request.POST or None, instance=ingredient)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Nguyên liệu đã được cập nhật!')
            return redirect('ingredient_list')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin vừa nhập.')

    return render(
        request,
        'ingredients/ingredient_form.html',
        {'ingredient': ingredient, 'form': form},
    )


@login_required
@ingredient_access_required
def ingredient_restock(request, ingredient_id):
    """Nhập thêm nguyên liệu."""
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

    return render(
        request,
        'ingredients/ingredient_restock.html',
        {'ingredient': ingredient, 'form': form},
    )


def _log_restock_action(
    request,
    ingredient: Ingredient,
    added_qty: Decimal,
    before_qty: Decimal,
    before_restock_date,
    total_value: Decimal,
):
    """Ghi log nhập kho vào bảng audit_logs."""
    try:
        data_old = {
            'quantity': str(before_qty),
            'last_restock_date': before_restock_date.isoformat() if before_restock_date else None,
        }
        data_new = {
            'added_quantity': str(added_qty),
            'new_quantity': str(ingredient.quantity),
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
        return
