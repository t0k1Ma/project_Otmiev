
from django.db import models
from django.conf import settings

EXTRA_SERVICES_CATALOG = {
    'window_cleaning': {
        'name': 'Мытье окон',
        'price': 300,
        'unit': 'за одно окно',
        'description': 'Мытье одного окна с двух сторон'
    },
    'sofa_cleaning': {
        'name': 'Химчистка дивана/ковра',
        'price': 750,
        'unit': 'за 1 штуку',
        'description': 'Химчистка одного дивана или ковра'
    },
    'fridge_cleaning': {
        'name': 'Мытье холодильника',
        'price': 300,
        'unit': 'за 1 штуку',
        'description': 'Полная мойка холодильника внутри и снаружи'
    },
    'oven_cleaning': {
        'name': 'Мытье духовки',
        'price': 400,
        'unit': 'за 1 штуку',
        'description': 'Чистка духового шкафа'
    }
}

BASE_PRICES_PER_SQM = {
    'standard': 25,      
    'general': 40,       
    'after_repair': 60,  
    'office': 55,        
}

class Order(models.Model):

    #Модель закакза
    
    CLEANING_TYPES = (
        ('standard', 'Стандартная уборка'),
        ('general', 'Генеральная уборка'),
        ('after_repair', 'После ремонта'),
        ('office', 'Офисная уборка'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    )
    
    URGENCY_CHOICES = (
        ('normal', 'Обычный'),
        ('urgent', 'Срочный'),
    )
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_orders',
        verbose_name='Заказчик'
    )
    
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_orders',
        verbose_name='Исполнитель'
    )
    
    
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    
    cleaning_type = models.CharField(
        max_length=20, 
        choices=CLEANING_TYPES,
        verbose_name='Тип уборки'
    )
    
    
    area_sqm = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        verbose_name='Площадь (кв.м)'
    )
    rooms_count = models.IntegerField(default=1, verbose_name='Комнат')
    
    
    address = models.CharField(max_length=255, verbose_name='Адрес')
    district = models.CharField(max_length=100, verbose_name='Район')
    
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        blank=True, null=True, verbose_name='Широта'
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        blank=True, null=True, verbose_name='Долгота'
    )
    
    
    scheduled_date = models.DateTimeField(
        verbose_name='Дата и время уборки'
    )
    
    
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Базовая цена (руб.)',
        help_text='Рассчитывается автоматически: площадь × цена за м²',
        editable=False
    )
    
    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default='normal',
        verbose_name='Срочность'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус'
    )
    
    
    extra_services = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Доп. услуги',
        help_text='Пример: [{"service": "window_cleaning", "quantity": 3}]'
    )
    
    extra_services_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Сумма доп. услуг',
        editable=False
    )
    
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Итоговая цена',
        editable=False
    )
    
    photos = models.JSONField(
        blank=True, null=True,
        verbose_name='Фотографии'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    completed_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name='Завершен'
    )
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.title}"
    
    #АВТОМАТИЧЕСКИЙ РАСЧЕТ ЦЕНЫ ПРИ СОХРАНЕНИИ 
    
    def save(self, *args, **kwargs):
        self.calculate_total_price()
        super().save(*args, **kwargs)
    
    # 
    
    def calculate_total_price(self):
        """
        Рассчитывает итоговую цену заказа:
        Базовая цена (площадь * цена за м²) + Доп. услуги
        """
        base_price_per_sqm = BASE_PRICES_PER_SQM.get(self.cleaning_type, 0)
        base_price = base_price_per_sqm * self.area_sqm
        
        self.price = base_price
        
        extra_total = 0
        if self.extra_services:
            for item in self.extra_services:
                service_key = item.get('service')
                quantity = item.get('quantity', 1)
                
                if service_key in EXTRA_SERVICES_CATALOG:
                    service_price = EXTRA_SERVICES_CATALOG[service_key]['price']
                    extra_total += service_price * quantity
        
        #
        self.extra_services_total = extra_total
        self.total_price = base_price + extra_total
        
        return self.total_price
    
    def get_extra_services_list(self):
        """
        Возвращает красивый список услуг с названиями и ценами
        """
        if not self.extra_services:
            return []
        
        result = []
        for item in self.extra_services:
            service_key = item.get('service')
            quantity = item.get('quantity', 1)
            
            if service_key in EXTRA_SERVICES_CATALOG:
                service = EXTRA_SERVICES_CATALOG[service_key]
                total = service['price'] * quantity
                
                result.append({
                    'name': service['name'],
                    'price': service['price'],
                    'quantity': quantity,
                    'total': total
                })
        
        return result
    
    def get_price_breakdown(self):
        """
        Возвращает подробную разбивку цены
        """
        base_price_per_sqm = BASE_PRICES_PER_SQM.get(self.cleaning_type, 0)
        base_price = base_price_per_sqm * self.area_sqm
        
        cleaning_type_name = self.get_cleaning_type_display()
        
        breakdown = {
            'cleaning_type': cleaning_type_name,
            'area_sqm': float(self.area_sqm),
            'price_per_sqm': base_price_per_sqm,
            'base_price': float(base_price),
            'extra_services': self.get_extra_services_list(),
            'extra_total': float(self.extra_services_total),
            'total': float(self.total_price)
        }
        
        return breakdown