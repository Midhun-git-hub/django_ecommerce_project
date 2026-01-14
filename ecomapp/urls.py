from django.urls import path
from.import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    
    path('',views.index,name='index'),
    
    path('product_list/',views.product_list,name='product_list'),
    
    path('product_detail/<int:id>/',views.product_detail,name='product_detail'),
    
    path('register/',views.register,name='register'),

    path('login/',views.login_view,name='login'),

    path('logout/',views.logout_view,name='logout'),
    
    path('add_to_cart/<int:id>/',views.add_to_cart,name='add_to_cart'),

    path('cart_page/',views.cart_page,name='cart_page'),
    
    path('increase_quantity/<int:id>/',views.increase_quantity,name='increase_quantity'),
    
    path('decrease_quantity/<int:id>/',views.decrease_quantity,name='decrease_quantity'),
    
    path('remove_from_cart/<int:id>/',views.remove_from_cart,name='remove_from_cart'),

    path('checkout/',views.checkout,name='checkout'),
    
    path('add_address/',views.add_address,name='add_address'),
    
    path('order_success/',views.order_success,name='order_success'),
    
    path('orders/',views.orders,name='orders'),
    
    path('category/<slug:slug>/',views.category_products,name='category_products'),
    
    path('about/',views.about,name='about'),
    
    path('contact/',views.contact,name='contact'),
    
    path('view_cart/',views.view_cart,name='view_cart'),
    
    path('view_address/',views.view_address,name='view_address'),
    
    path('edit_address/<int:id>/',views.edit_address,name='edit_address'),
    
    path('delete_address/<int:id>/',views.delete_address,name='delete_address'),
    
    path('profile_page/',views.profile_page,name='profile_page'),
    
    path('password_change/',auth_views.PasswordChangeView.as_view(
        template_name='change_password.html',
        success_url='/profile_page/'
        ),name='password_change'),
    
    path(
        'forgot-password/',
        auth_views.PasswordResetView.as_view(
            template_name='auth/forgot_password.html',
            email_template_name='auth/password_reset_email.html',
            subject_template_name='auth/password_reset_subject.txt',
            success_url='/forgot-password/done/'
        ),
        name='password_reset'
    ),

    # 📬 Email sent page
    path(
        'forgot-password/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='auth/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    # 🔁 Reset password link
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='auth/password_reset_confirm.html',
            success_url='/login/'
        ),
        name='password_reset_confirm'
    ),

    # ✅ Reset complete
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='auth/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    
    path('admin_orders/',views.admin_orders,name='admin_orders'),
    
    path('update_order_status/<int:id>/', views.update_order_status, name='update_order_status'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
