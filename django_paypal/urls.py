"""
URL configuration for django_paypal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

# Item_project/urls.py

from payment import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('items/', views.Items_list, name='Items_list'),
    path('Items/<int:Item_id>/', views.Item_detail, name='Item_detail'),
    path('Items/<int:Item_id>/create-order/', views.create_order, name='create_order'),
    path('Items/<int:Item_id>/payment-success/', views.payment_success, name='payment_success'),
    path('Items/<int:Item_id>/payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
