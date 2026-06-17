from django.urls import path
from . import views

urlpatterns = [
    #Заказы
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/activate/', views.ActivatePlacementView.as_view(), name='activate-placement'),
    path('my-orders/', views.MyOrdersView.as_view(), name='my-orders'),

    #Отклики
    path('orders/<int:order_id>/applications/', views.OrderApplicationListView.as_view(), name='order-applications'),
    path('applications/create/', views.OrderApplicationCreateView.as_view(), name='application-create'),
    path('applications/<int:pk>/accept/', views.AcceptApplicationView.as_view(), name='accept-application'),
    path('my-applications/', views.MyApplicationsView.as_view(), name='my-applications'),

    #Отзывы
    path('reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/executor/<int:executor_id>/', views.ReviewListView.as_view(), name='executor-reviews'),
    path('my-reviews/', views.MyReviewsView.as_view(), name='my-reviews'),

    
]