import base64
import requests
from datetime import datetime
from decouple import config

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.contrib.auth.models import User

from .models import Product, Category, Order, OrderItem
# Create your views here.
def dashboard(request):
    products = Product.objects.select_related('category').all()
    low_stock = [p for p in products if p.is_low_stock()]
    
    return render(request,'shop/dashboard.html',
                  {'products':products,
                   'low_stock':low_stock})

def product_create(request):
    if request.method == 'POST':
        Product.objects.create(
            name=request.POST['name'],
            category_id=request.POST['category'],
            price=request.POST['price'],
            stock=request.POST['stock'],
            image=request.FILES.get('image'),
        )
        return redirect('dashboard')
    categories = Category.objects.all()
    return render(request, 'shop/product_form.html', {'categories': categories})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.category_id = request.POST['category']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        return redirect('dashboard')
    categories = Category.objects.all()
    return render(request, 'shop/product_form.html', {
        'categories': categories,
        'product': product,
    })

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

def order_create(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        quantity = int(request.POST['quantity'])
        phone = request.POST['phone']
        order = Order.objects.create(user=request.user if request.user.is_authenticated else User.objects.first())
        OrderItem.objects.create(order=order, product=product, quantity=quantity)

        # Placeholder for M-Pesa STK Push — see initiate_mpesa_payment() below
        initiate_mpesa_payment(phone=phone, amount=product.price * quantity, order=order)

        return redirect('order_confirmation', pk=order.id)

    return render(request, 'shop/order_form.html', {'product': product})


def order_confirmation(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'shop/order_confirmation.html', {'order': order})

def index(request):
    return render(request, 'shop/index.html')

def about(request):
    featured_products = Product.objects.select_related('category').order_by('-id')[:5]
    return render(request, 'shop/about.html', {'featured_products': featured_products})


def get_mpesa_token():
    consumer_key = config('MPESA_CONSUMER_KEY')
    consumer_secret = config('MPESA_CONSUMER_SECRET')
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    print("STATUS:", response.status_code)
    print("BODY:", response.text)
    return response.json()['access_token']


def initiate_mpesa_payment(phone, amount, order):
    token = get_mpesa_token()
    shortcode = config('MPESA_SHORTCODE')
    passkey = config('MPESA_PASSKEY')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f'{shortcode}{passkey}{timestamp}'.encode()).decode()

    headers = {'Authorization': f'Bearer {token}'}
    payload = {
        'BusinessShortCode': shortcode,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': int(amount),
        'PartyA': phone,
        'PartyB': shortcode,
        'PhoneNumber': phone,
        'CallBackURL': config('MPESA_CALLBACK_URL'),
        'AccountReference': f'Order{order.id}',
        'TransactionDesc': f'Payment for order #{order.id}',
    }

    url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
