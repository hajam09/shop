from django.urls import path

from core.views import hello_view

app_name = 'core'

urlpatterns = [
    path('', hello_view, name='hello'),
]
