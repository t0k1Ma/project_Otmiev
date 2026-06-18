from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Order, Payment, Review, OrderApplication
from .serializers import OrderSerializer, OrderCreateSerializer, PaymentSerializer, ReviewSerializer, ReviewCreateSerializer, OrderApplicationSerializer, OrderApplicationCreateSerializer


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Order.objects.filter(
            status='published',
            placement_paid_until__gte=timezone.now()
        ).order_by('-urgency', '-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Order.objects.all()


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class ActivatePlacementView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        order = self.get_object()
        
        if order.customer != request.user:
            return Response({'error': 'Это не ваш заказ'}, status=403)
        
        tariff = request.data.get('tariff')
        if not tariff:
            return Response({'error': 'Укажите тариф'}, status=400)
        
        try:
            paid_until = order.activate_placement(tariff)
            return Response({
                'message': 'Размещение активировано',
                'paid_until': paid_until,
                'order': OrderSerializer(order).data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=400)


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)
    
class CompleteOrderView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    
    def post(self, request, pk):
        order = self.get_object()
        
        if order.customer != request.user:
            return Response(
                {'error': 'Только заказчик может завершить заказ'},
                status=403
            )
        
        if order.status != 'in_progress':
            return Response(
                {'error': 'Можно завершить только заказ в работе'},
                status=400
            )
        
        order.complete_order()
        return Response({
            'message': 'Заказ завершен',
            'order': OrderSerializer(order).data
        })


class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        executor_id = self.kwargs.get('executor_id')
        if executor_id:
            return Review.objects.filter(executor_id=executor_id)
        return Review.objects.all()


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class MyReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(customer=self.request.user)
    

class OrderApplicationListView(generics.ListAPIView):
    serializer_class = OrderApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        order = Order.objects.get(id=order_id)
        
        if order.customer != self.request.user:
            return OrderApplication.objects.none()
        
        return OrderApplication.objects.filter(order=order)


class OrderApplicationCreateView(generics.CreateAPIView):
    serializer_class = OrderApplicationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(executor=self.request.user)


class AcceptApplicationView(generics.GenericAPIView):
    serializer_class = OrderApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = OrderApplication.objects.all()
    
    def post(self, request, pk):
        application = self.get_object()
        order = application.order
        
        if order.customer != request.user:
            return Response(
                {'error': 'Только заказчик может принять отклик'},
                status=403
            )
        
        if order.status != 'published':
            return Response(
                {'error': 'Заказ должен быть в статусе "Опубликован"'},
                status=400
            )
        
        order = application.accept()
        
        return Response({
            'message': 'Исполнитель назначен',
            'order': OrderSerializer(order).data
        })


class MyApplicationsView(generics.ListAPIView):
    serializer_class = OrderApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OrderApplication.objects.filter(executor=self.request.user)