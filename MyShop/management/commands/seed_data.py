import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from MyShop.models import Category, Product, Order, OrderItem


class Command(BaseCommand):
    help = 'Seeds the database with sample categories, products, and orders for demos.'

    def handle(self, *args, **kwargs):
        categories = ['Electronics', 'Groceries', 'Clothing']
        cat_objs = [Category.objects.get_or_create(name=name)[0] for name in categories]

        products = [
            ('Wireless Mouse', cat_objs[0], 19.99, 3),
            ('Bluetooth Speaker', cat_objs[0], 45.00, 12),
            ('USB-C Cable', cat_objs[0], 9.99, 2),
            ('Rice 2kg', cat_objs[1], 5.50, 40),
            ('Cooking Oil 1L', cat_objs[1], 4.20, 4),
            ('T-Shirt', cat_objs[2], 12.00, 25),
            ('Jeans', cat_objs[2], 35.00, 8),
        ]
        product_objs = []
        for name, category, price, stock in products:
            p, _ = Product.objects.get_or_create(
                name=name, category=category,
                defaults={'price': price, 'stock': stock}
            )
            product_objs.append(p)

        user, _ = User.objects.get_or_create(username='demo', defaults={'is_staff': True})
        user.set_password('demo1234')
        user.save()

        now = timezone.now()
        for i in range(10):
            order = Order.objects.create(user=user, created_at=now - timedelta(days=random.randint(0, 6)))
            for _ in range(random.randint(1, 3)):
                OrderItem.objects.create(
                    order=order,
                    product=random.choice(product_objs),
                    quantity=random.randint(1, 5),
                )

        self.stdout.write(self.style.SUCCESS('Seed data created: 3 categories, 7 products, 10 orders.'))