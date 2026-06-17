from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/activate/', views.ActivatePlacementView.as_view(), name='activate-placement'),
    path('my-orders/', views.MyOrdersView.as_view(), name='my-orders'),
]