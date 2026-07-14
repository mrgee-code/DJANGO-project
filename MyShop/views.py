from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from .models import Product, Category, Order

# Create your views here.
def dashboard(request):
    products = Product.objects.select_related('category').all()
    low_stock = [p for p in products if p.is_low_stock()]
    
    return render(request,'shop/dashboard.html',
                  {'products':products,
                   'low_stock':low_stock})

def product_create(request):
    if request.method== 'POST':
        Product.objects.create(
            name=request.POST['name'],
            category_id=request.POST['category'],
            price=request.POST['price'],
            stock=request.POST['stock'],
        )
        return redirect('dashboard')
    Categories=Category.objects.all()
    return render(request,'shop/product.html', 
                  {'categories':Categories})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method =='POST':
        product.name = request.POST['name']
        product.category_id = request.POST['category']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.save()
        return redirect('dashboard')
    categories=Category.objects.all()
    return render(request,'shop/product_form.html',
                  {'categories':categories,
                   'product':product,})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('dashboard')

def orders_chart_data(request):
    data = (
        Order.objects
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    return JsonResponse({
        'labels':[str(d['day']) for d in data],
        'counts':[d['count'] for d in data],
    })

