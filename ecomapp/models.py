from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# used to group products
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    
    def __str__(self):
        return self.name

# used to store product details
class Product(models.Model):
    name=models.CharField(max_length=200)
    description=models.TextField()
    price=models.DecimalField(max_digits=10, decimal_places=2)
    stock=models.IntegerField()
    category=models.ForeignKey(Category, on_delete=models.CASCADE)
    product_image=models.ImageField(upload_to='products/')
    is_active=models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
# used for cart
class Cart(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cart {self.id}-{self.user.username}"
    
# used for cart items
class CartItem(models.Model):
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    
    @property
    def total_price(self):
        return self.product.price * self.quantity


#used for addresses
class Address(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    fullname=models.CharField(max_length=200)
    address=models.TextField()
    phone=models.CharField(max_length=15)
    city=models.CharField(max_length=100)
    pincode=models.CharField(max_length=20)
    
    def __str__(self):
        return f"Address of {self.user.username} - {self.city} ({self.pincode})"
    
    
# used for orders and payment
class Order(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    total_price=models.DecimalField(max_digits=10, decimal_places=2)
    status=models.CharField(
        choices=[
            ('PENDING', 'Pending'),
            ('PAID', 'Paid'),
            ('SHIPPED', 'Shipped'),
            ('DELIVERED', 'Delivered'),
        ],
        max_length=20,
        default='PENDING'
    )
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.id}-{self.user.username}"
    
# used for order items
class OrderItem(models.Model):
    order=models.ForeignKey(Order,related_name='items', on_delete=models.CASCADE)
    product_name=models.CharField(max_length=100)
    product_image = models.ImageField(upload_to='order_items/',blank=True,null=True)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    quantity=models.IntegerField()
    
    def __str__(self):
        return f"{self.product_name}(order {self.order.id})"
    
    @property
    def get_total(self):
        return self.price * self.quantity
    
#used for payment
class Payment(models.Model):
    order=models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_id=models.CharField(max_length=200)
    method=models.CharField(max_length=50)
    status=models.CharField(max_length=50)
    
    def __str__(self):
        return f"Payment for Order {self.order.id}-{self.status}"
    
# used for reviews
class Review(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE,related_name='reviews')    
    rating=models.IntegerField()
    comment=models.TextField()
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name} ({self.rating}⭐)"
    
# used for contact messages
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"