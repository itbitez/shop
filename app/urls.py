from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('shop/', views.shop, name='shop'),
    path('cart/', views.cart_view, name='cart'),
    path('quickview/<int:product_id>/', views.quickview, name='quickview'),
    path('login/', views.auth, name='login'),
    path('my-account/', views.my_account, name='account'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Cart
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>/',
         views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/',
         views.item_decrement, name='item_decrement'),
    path('cart/cart_clear/', views.cart_clear, name='cart_clear'),
    path('cart/cart-detail/',views.cart_detail,name='cart_detail'),
    
    # Checkout
    path('checkout/', views.checkout_page, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),
    path('order-successful/', views.thanks, name='thank-you'),
    path('account/', views.account_view, name='account'),
]
