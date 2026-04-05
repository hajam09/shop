from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('addresses/', views.address_book, name='address_book'),
    path('addresses/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
]
