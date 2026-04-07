from django.urls import path

from catalog import views

app_name = 'catalog'

urlpatterns = [
    path('category/', views.categoryView, name='category-view'),
    path('category/<int:pk>/edit/', views.categoryEditView, name='category-edit'),
    path('category/<int:pk>/delete/', views.categoryDeleteView, name='category-delete'),
    path('search/', views.productSearchView, name='product-search'),
    path('product/<slug:slug>/', views.productDetailView, name='product-detail'),
    path('product/<slug:slug>/add-to-cart/', views.addToCartView, name='add-to-cart'),
]
