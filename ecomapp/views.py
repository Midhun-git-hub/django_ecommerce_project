from django.shortcuts import render,redirect
from . models import *
from . forms import *
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from datetime import datetime
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
import razorpay
# Create your views here.

# home page view
def index(request):
    categories = Category.objects.all()# used to add category list in navbar
    products = Product.objects.filter(is_active=True)[:8]
    return render(request, 'index.html', {'categories': categories, 'products': products, 'year':datetime.now().year})


# product list view with search functionality
@login_required
def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories=Category.objects.all()# used to add category list in navbar
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    return render(request, 'product_list.html',{'products': products, 'categories':categories,'query': query})


# product detail view with review functionality
@login_required
def product_detail(request, id):
    categories=Category.objects.all()# used to add category list in navbar
    product = Product.objects.get(id=id)
    reviews=Review.objects.all()
    form=ReviewForm()
    if request.method=="POST":
        if not request.user.is_authenticated:
            return redirect('login')
        if Review.objects.filter(user=request.user, product=product).exists():
            messages.warning(request, "You have already reviewed this product.")
            return redirect('product_detail', id=id)
        form=ReviewForm(request.POST)
        if form.is_valid():
            review=form.save(commit=False)
            review.user=request.user
            review.product=product
            review.save()
            messages.success(request, "Your review has been submitted successfully.")
            return redirect('product_detail', id=id)
    return render(request, 'product_detail.html', {'product': product, 'categories': categories, 'reviews': reviews, 'form': form})


# user registration view
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


# user login view
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


# user logout view
def logout_view(request):
    logout(request)
    return redirect('index')


# add to cart view
@login_required
def add_to_cart(request, id):
    products=Product.objects.get(id=id)
    cart,created=Cart.objects.get_or_create(user=request.user)
    cart_item,created=CartItem.objects.get_or_create(cart=cart,product=products)
    if not created:
        cart_item.quantity+=1
        cart_item.save()
    return redirect('cart_page')


# cart page view
@login_required
def cart_page(request):
    cart,created=Cart.objects.get_or_create(user=request.user)
    cart_items=CartItem.objects.filter(cart=cart)
    total_price=sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})



# increase cart item quantity
@login_required
def increase_quantity(request, id):
    cart_item = CartItem.objects.get(id=id, cart__user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_page')


# decrease cart item quantity
@login_required
def decrease_quantity(request, id):
    cart_item=CartItem.objects.get(id=id, cart__user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_page')


# remove item from cart
@login_required
def remove_from_cart(request, id):
    cart_item = CartItem.objects.get(id=id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_page')


# checkout view
@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        return redirect('cart_page')

    total = sum(item.total_price for item in cart_items)

    if not Address.objects.filter(user=request.user).exists():
        messages.warning(request, "Please add a delivery address before checkout.")
        return redirect('add_address')

    if request.method == "POST":
        address_id = request.POST.get("address")
        address = Address.objects.get(id=address_id, user=request.user)

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_name=item.product.name,
                product_image=item.product.product_image,
                price=item.product.price,
                quantity=item.quantity
            )

        cart_items.delete()  # clear cart

        return redirect('order_success')

    addresses = Address.objects.filter(user=request.user)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'addresses': addresses
    })



# order success page
@login_required
def order_success(request):
    return render(request, 'order_success.html')



# adding address for delivery
@login_required
def add_address(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        address_text = request.POST.get("address")
        phone= request.POST.get("phone")
        city= request.POST.get("city")
        pincode= request.POST.get("pincode")

        Address.objects.create(
            user=request.user,
            fullname=fullname,
            address=address_text,
            phone=phone,
            city=city,
            pincode=pincode
        )

        return redirect('checkout')

    return render(request, 'add_address.html')


# orders view for users
@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    categories=Category.objects.all()  # used to add category list in navbar
    return render(request, 'orders.html', {'orders': orders, 'categories': categories})


# products by category view
@login_required
def category_products(request, slug):
    category = Category.objects.get(slug=slug)
    categories=Category.objects.all()  # used to add category list in navbar
    products = Product.objects.filter(category=category, is_active=True)
    return render(request, 'product_list.html', {'products': products, 'category': category, 'categories': categories})


# about us page
def about(request):
    categories=Category.objects.all()# used to add category list in navbar
    return render(request, 'about.html', {'categories': categories})


# contact us page with form handling and email acknowledgment(auto-replay)
@login_required
def contact(request):
    categories=Category.objects.all()# used to add category list in navbar
    if request.method == "POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        subject=request.POST.get("subject")
        message=request.POST.get("message")
        Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        send_mail(
            subject="We received your message",
            message=f"Hi {name},\n\nWe have received your message. Our Crew will contact you shortly.\n\n— WB Crew 🏴‍☠️",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        messages.success(request, "Your message has been sent successfully! Our crew will get back to you soon.")
    return render(request, 'contact.html', {'categories': categories})


# view cart details
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


# view addresses
@login_required
def view_address(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'view_address.html', {'addresses': addresses})


# edit address
@login_required
def edit_address(request, id):
    address = Address.objects.get(id=id, user=request.user)
    if request.method == "POST":
        address.fullname = request.POST.get("fullname")
        address.address = request.POST.get("address")
        address.phone = request.POST.get("phone")
        address.city = request.POST.get("city")
        address.pincode = request.POST.get("pincode")
        address.save()
        return redirect('view_address')
    return render(request, 'edit_address.html', {'address': address})


# delete address
@login_required
def delete_address(request, id):
    address = Address.objects.get(id=id, user=request.user)
    address.delete()
    return redirect('view_address')


# profile page view
@login_required
def profile_page(request):
    return render(request, 'profile.html')


# admin view to see all orders
@staff_member_required
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_orders.html', {'orders': orders})


# admin view to update order status
@staff_member_required
def update_order_status(request, id):
    order = Order.objects.get(id=id)
    order_items = OrderItem.objects.filter(order=order)
    if request.method == "POST":
        status = request.POST.get("status")
        order.status = status
        order.save()
        return redirect('admin_orders')
    return render(request, 'update_order_status.html', {'order': order, 'order_items': order_items})