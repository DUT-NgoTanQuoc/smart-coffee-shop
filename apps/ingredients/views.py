from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ingredient
from apps.core.decorators import manager_required


@login_required
def ingredient_list(request):
    """Danh sách nguyên liệu"""
    ingredients = Ingredient.objects.all().order_by('name')
    
    # Lọc nguyên liệu sắp hết
    low_stock_only = request.GET.get('low_stock')
    if low_stock_only:
        ingredients = [i for i in ingredients if i.is_low_stock()]
    
    context = {
        'ingredients': ingredients,
    }
    
    return render(request, 'ingredients/ingredient_list.html', context)


@login_required
@manager_required
def ingredient_create(request):
    """Tạo nguyên liệu mới"""
    if request.method == 'POST':
        try:
            ingredient = Ingredient()
            ingredient.name = request.POST.get('name')
            ingredient.unit = request.POST.get('unit')
            ingredient.quantity = request.POST.get('quantity', 0)
            ingredient.min_quantity = request.POST.get('min_quantity', 0)
            ingredient.price_per_unit = request.POST.get('price_per_unit')
            ingredient.supplier = request.POST.get('supplier', '')
            
            ingredient.save()
            
            messages.success(request, 'Nguyên liệu đã được tạo thành công!')
            return redirect('ingredient_list')
            
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return render(request, 'ingredients/ingredient_form.html')


@login_required
@manager_required
def ingredient_update(request, ingredient_id):
    """Cập nhật nguyên liệu"""
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    
    if request.method == 'POST':
        try:
            ingredient.name = request.POST.get('name')
            ingredient.unit = request.POST.get('unit')
            ingredient.quantity = request.POST.get('quantity')
            ingredient.min_quantity = request.POST.get('min_quantity')
            ingredient.price_per_unit = request.POST.get('price_per_unit')
            ingredient.supplier = request.POST.get('supplier', '')
            
            ingredient.save()
            
            messages.success(request, 'Nguyên liệu đã được cập nhật!')
            return redirect('ingredient_list')
            
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    context = {
        'ingredient': ingredient,
    }
    
    return render(request, 'ingredients/ingredient_form.html', context)


@login_required
@manager_required
def ingredient_restock(request, ingredient_id):
    """Nhập thêm nguyên liệu"""
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    
    if request.method == 'POST':
        try:
            quantity_to_add = float(request.POST.get('quantity', 0))
            ingredient.add_stock(quantity_to_add)
            
            # Cập nhật ngày nhập hàng
            from django.utils import timezone
            ingredient.last_restock_date = timezone.now().date()
            ingredient.save()
            
            messages.success(request, f'Đã nhập thêm {quantity_to_add} {ingredient.unit}')
            return redirect('ingredient_list')
            
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    context = {
        'ingredient': ingredient,
    }
    
    return render(request, 'ingredients/ingredient_restock.html', context)
