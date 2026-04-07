from django.urls import path

from checkout import views

app_name = 'checkout'

urlpatterns = [
    path('cart/', views.cartView, name='cart'),
    path('cart/clear/', views.cartClearView, name='cart-clear'),
    path('cart/checkout/', views.cartCheckoutView, name='cart-checkout'),
]

