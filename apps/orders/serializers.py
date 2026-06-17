from rest_framework import serializers
from .models import Order, Payment, Review, OrderApplication
from apps.users.serializers import UserSerializer



class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    executor = UserSerializer(read_only=True)
    extra_services_list = serializers.SerializerMethodField()
    price_breakdown = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'executor', 'title', 'description',
            'cleaning_type', 'area_sqm', 'rooms_count', 'address', 'city',
            'latitude', 'longitude', 'scheduled_date', 'price', 'urgency',
            'urgency_fee', 'status', 'placement_tariff', 'placement_price',
            'placement_paid_until', 'extra_services', 'extra_services_total',
            'total_price', 'photos', 'created_at', 'updated_at',
            'extra_services_list', 'price_breakdown', 'distance'
        ]
        read_only_fields = [
            'price', 'urgency_fee', 'extra_services_total', 'total_price',
            'placement_price', 'placement_paid_until', 'published_at',
            'latitude', 'longitude'
        ]

    def get_distance(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            if hasattr(user, 'executor_profile'):
                profile = user.executor_profile
                if profile.latitude and profile.longitude and obj.latitude and obj.longitude:
                    from apps.orders.utils import calculate_distance
                    distance = calculate_distance(
                        profile.latitude, profile.longitude,
                        obj.latitude, obj.longitude
                    )
                    return f"{distance} км"
        return None
    
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


# ... (весь предыдущий код)

class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    executor_name = serializers.CharField(source='executor.username', read_only=True)
    order_title = serializers.CharField(source='order.title', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'order', 'order_title', 'customer', 'customer_name',
            'executor', 'executor_name', 'rating', 'comment', 'photos',
            'created_at'
        ]
        read_only_fields = ['customer', 'executor', 'order']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['order', 'rating', 'comment', 'photos']
    
    def validate_order(self, value):
        if value.status != 'completed':
            raise serializers.ValidationError("Можно оставить отзыв только к завершенному заказу")
        
        if Review.objects.filter(order=value).exists():
            raise serializers.ValidationError("Отзыв к этому заказу уже оставлен")
        
        return value
    
    def create(self, validated_data):
        order = validated_data['order']
        validated_data['customer'] = order.customer
        validated_data['executor'] = order.executor
        return super().create(validated_data)
   
class OrderApplicationSerializer(serializers.ModelSerializer):
    executor_name = serializers.CharField(source='executor.username', read_only=True)
    executor_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderApplication
        fields = [
            'id', 'order', 'executor', 'executor_name', 'executor_rating',
            'message', 'proposed_price', 'status', 'created_at', 'reviewed_at'
        ]
        read_only_fields = ['executor', 'status', 'reviewed_at']
    
    def get_executor_rating(self, obj):
        if hasattr(obj.executor, 'executor_profile'):
            return obj.executor.executor_profile.rating
        return 0


class OrderApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderApplication
        fields = ['order', 'message', 'proposed_price']
    
    def validate_order(self, value):
        if value.status != 'published':
            raise serializers.ValidationError("Можно откликнуться только на опубликованный заказ")
        
        if OrderApplication.objects.filter(
            order=value,
            executor=self.context['request'].user
        ).exists():
            raise serializers.ValidationError("Вы уже откликнулись на этот заказ")
        
        return value
    
    def create(self, validated_data):
        validated_data['executor'] = self.context['request'].user
        return super().create(validated_data)