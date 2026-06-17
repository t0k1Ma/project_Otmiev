from rest_framework import serializers
from .models import Order, Payment
from apps.users.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    executor = UserSerializer(read_only=True)
    extra_services_list = serializers.SerializerMethodField()
    price_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'executor', 'title', 'description',
            'cleaning_type', 'area_sqm', 'rooms_count', 'address', 'district',
            'latitude', 'longitude', 'scheduled_date', 'price', 'urgency',
            'urgency_fee', 'status', 'placement_tariff', 'placement_price',
            'placement_paid_until', 'extra_services', 'extra_services_total',
            'total_price', 'photos', 'created_at', 'updated_at',
            'extra_services_list', 'price_breakdown'
        ]
        read_only_fields = [
            'price', 'urgency_fee', 'extra_services_total', 'total_price',
            'placement_price', 'placement_paid_until', 'published_at'
        ]
    
    def get_extra_services_list(self, obj):
        return obj.get_extra_services_list()
    
    def get_price_breakdown(self, obj):
        return obj.get_price_breakdown()


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'title', 'description', 'cleaning_type', 'area_sqm', 'rooms_count',
            'address', 'district', 'latitude', 'longitude', 'scheduled_date',
            'urgency', 'extra_services', 'photos'
        ]
    
    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        order = Order.objects.create(**validated_data)
        return order


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'customer', 'amount', 'tariff', 'tariff_name', 
                  'paid_until', 'status', 'created_at']
        read_only_fields = ['customer', 'amount', 'tariff', 'tariff_name', 'paid_until']