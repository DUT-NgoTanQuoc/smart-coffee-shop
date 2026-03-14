from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Recipe, Customization
from apps.core.decorators import manager_required


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
@manager_required
def product_create(request):
    """Tạo sản phẩm mới"""
    if request.method == 'POST':
        # Xử lý tạo sản phẩm
        # Code đơn giản, trong thực tế nên dùng Django Forms
        try:
            product = Product()
            product.name = request.POST.get('name')
            product.description = request.POST.get('description', '')
            
            category_id = request.POST.get('category')
            if category_id:
                product.category_id = category_id
            
            product.price_small = request.POST.get('price_small')
            product.price_medium = request.POST.get('price_medium')
            product.price_large = request.POST.get('price_large')
            
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                product.image.save(image_file.name, image_file, save=False)
                product.save()
            
            product.save()
            
            messages.success(request, 'Sản phẩm đã được tạo thành công!')
            return redirect('product_detail', product_id=product.id)
            
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'products/product_form.html', context)


@login_required
@manager_required
def product_update(request, product_id):
    """Cập nhật sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            product.name = request.POST.get('name')
            product.description = request.POST.get('description', '')
            
            category_id = request.POST.get('category')
            if category_id:
                product.category_id = category_id
            
            product.price_small = request.POST.get('price_small')
            product.price_medium = request.POST.get('price_medium')
            product.price_large = request.POST.get('price_large')
            
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                product.image.save(image_file.name, image_file, save=False)
                product.save()
            
            product.save()
            
            messages.success(request, 'Sản phẩm đã được cập nhật!')
            return redirect('product_detail', product_id=product.id)
            
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    categories = Category.objects.all()
    
    context = {
        'product': product,
        'categories': categories,
    }
    
    return render(request, 'products/product_form.html', context)


@login_required
@manager_required
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
