from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    #Настройка отображения заказов в админке
    
    # Какие колонки показывать в списке заказов
    list_display = (
        'id', 
        'title', 
        'customer', 
        'cleaning_type', 
        'total_price', 
        'status', 
        'scheduled_date'
    )
    
    # Фильтры справа (позволят быстро отсеять заказы по статусу, типу и т.д.)
    list_filter = ('status', 'cleaning_type', 'urgency', 'district')
    
    # Поиск сверху (можно искать по названию, адресу или логину заказчика)
    search_fields = ('title', 'address', 'customer__username')
    
    # Поля, которые можно редактировать прямо из общего списка
    list_editable = ('status',)