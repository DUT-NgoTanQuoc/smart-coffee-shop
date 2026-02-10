from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Customer, FavoriteDrink


@login_required
def customer_list(request):
    """Danh sách khách hàng"""
    customers = Customer.objects.all().order_by('-points')
    
    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        customers = customers.filter(
            models.Q(name__icontains=search) |
            models.Q(phone__icontains=search)
        )
    
    # Lọc theo tier
    tier = request.GET.get('tier')
    if tier:
        customers = customers.filter(tier=tier)
    
    context = {
        'customers': customers,
    }
    
    return render(request, 'customers/customer_list.html', context)


@login_required
def customer_detail(request, customer_id):
    """Chi tiết khách hàng"""
    customer = get_object_or_404(Customer, id=customer_id)
    orders = customer.orders.all().order_by('-order_date')[:10]
    favorite_drinks = customer.favorite_drinks.all()
    
    context = {
        'customer': customer,
        'orders': orders,
        'favorite_drinks': favorite_drinks,
    }
    
    return render(request, 'customers/customer_detail.html', context)


@login_required
def customer_create(request):
    """Tạo khách hàng mới"""
    if request.method == 'POST':
        try:
            customer = Customer()
            customer.name = request.POST.get('name')
            customer.phone = request.POST.get('phone')
            customer.email = request.POST.get('email', '')
            
            customer.save()
            
            messages.success(request, 'Khách hàng đã được tạo thành công!')
            return redirect('customer_detail', customer_id=customer.id)
            
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return render(request, 'customers/customer_form.html')
