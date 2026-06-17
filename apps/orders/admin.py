from django.contrib import admin
from .models import Order, Payment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'customer',
        'executor',
        'cleaning_type',
        'area_sqm',
        'total_price',
        'urgency',
        'status',
        'placement_paid_until',
        'created_at',
    )
    
    list_filter = (
        'status',
        'cleaning_type',
        'urgency',
        'district',
        'placement_tariff',
    )
    
    search_fields = (
        'title',
        'address',
        'customer__username',
        'customer__email',
        'district',
    )
    
    list_editable = ('status',)
    
    readonly_fields = (
        'price',
        'urgency_fee',
        'extra_services_total',
        'total_price',
        'placement_price',
        'created_at',
        'updated_at',
        'published_at',
    )
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'customer',
                'executor',
                'title',
                'description',
                'cleaning_type',
                'status',
            )
        }),
        ('Объект', {
            'fields': (
                'area_sqm',
                'rooms_count',
                'address',
                'district',
                'latitude',
                'longitude',
                'scheduled_date',
            )
        }),
        ('Цена', {
            'fields': (
                'price',
                'urgency',
                'urgency_fee',
                'extra_services',
                'extra_services_total',
                'total_price',
            )
        }),
        ('Размещение', {
            'fields': (
                'placement_tariff',
                'placement_price',
                'placement_paid_until',
            )
        }),
        ('Дополнительно', {
            'fields': (
                'photos',
                'created_at',
                'updated_at',
                'published_at',
                'completed_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('customer', 'executor')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'customer',
        'tariff_name',
        'amount',
        'status',
        'paid_until',
        'created_at',
    )
    
    list_filter = (
        'status',
        'tariff',
        'created_at',
    )
    
    search_fields = (
        'order__title',
        'customer__username',
        'customer__email',
    )
    
    readonly_fields = (
        'created_at',
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('order', 'customer')