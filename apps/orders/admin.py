from django.contrib import admin
from django import forms
from .models import Order, Payment, Review, OrderApplication
from .constants import EXTRA_SERVICES_CATALOG


class OrderAdminForm(forms.ModelForm):
    
    class Meta:
        model = Order
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем подсказку в поле extra_services
        services_help = "Формат JSON: [{\"service\": \"window_cleaning\", \"quantity\": 4}]\n\n"
        services_help += "Доступные услуги:\n"
        for key, service in EXTRA_SERVICES_CATALOG.items():
            services_help += f"  • {key} — {service['name']} ({service['price']} руб)\n"
        self.fields['extra_services'].help_text = services_help


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    
    list_display = (
        'id', 'title', 'customer', 'executor', 'cleaning_type',
        'area_sqm', 'total_price', 'urgency', 'status',
        'placement_paid_until', 'created_at',
    )
    
    list_filter = (
        'status', 'cleaning_type', 'urgency', 'city', 'placement_tariff',
    )
    
    search_fields = (
        'title', 'address', 'customer__username', 'customer__email', 'city',
    )
    
    list_editable = ('status',)
    
    readonly_fields = (
        'price', 'urgency_fee', 'extra_services_total', 'total_price',
        'placement_price', 'created_at', 'updated_at', 'published_at',
        'latitude', 'longitude'
    )
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'customer', 'executor', 'title', 'description',
                'cleaning_type', 'status',
            )
        }),
        ('Объект', {
            'fields': (
                'area_sqm', 'rooms_count', 'address', 'city',
                'latitude', 'longitude', 'scheduled_date',
            ),
            'description': 'Координаты заполняются автоматически по адресу'
        }),
        ('Цена', {
            'fields': (
                'price', 'urgency', 'urgency_fee', 'extra_services',
                'extra_services_total', 'total_price',
            )
        }),
        ('Размещение', {
            'fields': (
                'placement_tariff', 'placement_price', 'placement_paid_until',
            )
        }),
        ('Дополнительно', {
            'fields': (
                'photos', 'created_at', 'updated_at',
                'published_at', 'completed_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        if obj.placement_tariff and not obj.placement_paid_until:
            try:
                obj.activate_placement(obj.placement_tariff)
            except Exception as e:
                self.message_user(request, f"Ошибка активации: {e}", level='error')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('customer', 'executor')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'customer', 'tariff_name',
        'amount', 'status', 'paid_until', 'created_at',
    )
    
    list_filter = (
        'status', 'tariff', 'created_at',
    )
    
    search_fields = (
        'order__title', 'customer__username', 'customer__email',
    )
    
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('order', 'customer')
    
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'customer', 'executor', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('order__title', 'customer__username', 'executor__username', 'comment')
    readonly_fields = ('created_at',)

@admin.register(OrderApplication)
class OrderApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'executor', 'status', 'proposed_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__title', 'executor__username')
    readonly_fields = ('created_at', 'reviewed_at')