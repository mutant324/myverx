from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<slug:slug>/', views.catalog, name='catalog_cat'),
    path('product/<int:product_id>/', views.product_page, name='product'),
    path('search/', views.search, name='search'),
    # корзина
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/qty/<int:item_id>/', views.cart_qty, name='cart_qty'),
    # заказ и оплата
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/pay/', views.order_pay, name='order_pay'),
    path('order/<int:order_id>/paid/', views.order_paid, name='order_paid'),
    # профиль и вход
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
