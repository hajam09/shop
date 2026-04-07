from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('addresses/', views.address_book, name='address_book'),
    path('addresses/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('wishlist/', views.wishlistView, name='wishlist'),
    path('wishlist/add/<slug:slug>/', views.wishlistAddView, name='wishlist-add'),
    path('wishlist/remove/<slug:slug>/', views.wishlistRemoveView, name='wishlist-remove'),
    path('wishlist/clear/', views.wishlistClearView, name='wishlist-clear'),
]
