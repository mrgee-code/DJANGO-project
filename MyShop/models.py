from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Categories'

        def __str__(self):
            return self.name 
        
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)

    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold
    
    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total(self):
        return sum(item.subtotal() for item in self.orderitem_set.all())
    
    def __str__(self):
        return f'Order #{self.id} - {self.user}'
    
class OrderItem(models.Model):
    oder = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.price *self.quantity
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name}'