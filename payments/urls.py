from django.urls import path

from payments import views

app_name = 'payments'

urlpatterns = [
    path('payment-methods/', views.paymentMethodView, name='payment-method-view'),
    path('payment-methods/<int:pk>/edit/', views.paymentMethodEditView, name='payment-method-edit'),
    path('payment-methods/<int:pk>/delete/', views.paymentMethodDeleteView, name='payment-method-delete'),
]
