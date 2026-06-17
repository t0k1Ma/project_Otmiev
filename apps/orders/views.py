from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Order, Payment
from .serializers import OrderSerializer, OrderCreateSerializer, PaymentSerializer


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