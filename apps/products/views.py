from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Recipe, Customization
from .forms import ProductForm


@login_required
def product_list(request):
    """Danh sách sản phẩm"""
    products = Product.objects.all().select_related('category')
    
    # Lọc theo category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
    }
    
    return render(request, 'products/product_list.html', context)


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
