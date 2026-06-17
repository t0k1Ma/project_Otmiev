from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .constants import (
    EXTRA_SERVICES_CATALOG,
    BASE_PRICES_PER_SQM,
    PLACEMENT_TARIFFS,
    URGENCY_FEE,
    CLEANING_TYPES,
    ORDER_STATUS_CHOICES,
    URGENCY_CHOICES,
    TARIFF_CHOICES,
    PAYMENT_STATUS_CHOICES,
)


class Order(models.Model):
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
        editable=False
    )

    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default='normal',
        verbose_name='Срочность'
    )

    urgency_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Наценка за срочность',
        editable=False
    )

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='draft',
        verbose_name='Статус'
    )

    placement_tariff = models.CharField(
        max_length=20,
        choices=TARIFF_CHOICES,
        blank=True,
        null=True,
        verbose_name='Тариф размещения'
    )

    placement_paid_until = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Оплата размещения до'
    )

    placement_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Стоимость размещения (руб.)',
        editable=False
    )

    extra_services = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Доп. услуги'
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
        verbose_name='Итоговая цена заказа',
        editable=False
    )

    photos = models.JSONField(
        blank=True, null=True,
        verbose_name='Фотографии'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    published_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name='Опубликован'
    )
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

    @property
    def is_urgent(self):
        return self.urgency == 'urgent'

    @property
    def is_placement_active(self):
        if not self.placement_paid_until:
            return False
        return timezone.now() <= self.placement_paid_until

    def can_be_viewed_by_executors(self):
        return self.status == 'published' and self.is_placement_active

    def save(self, *args, **kwargs):
        self.calculate_total_price()
        super().save(*args, **kwargs)

    def calculate_total_price(self):
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
        self.extra_services_total = extra_total

        if self.urgency == 'urgent':
            self.urgency_fee = URGENCY_FEE
        else:
            self.urgency_fee = 0

        self.total_price = base_price + extra_total + self.urgency_fee
        return self.total_price

    def activate_placement(self, tariff_key):
        if tariff_key not in PLACEMENT_TARIFFS:
            raise ValueError(f"Неизвестный тариф: {tariff_key}")

        tariff = PLACEMENT_TARIFFS[tariff_key]

        self.placement_tariff = tariff_key
        self.placement_price = tariff['price']
        self.placement_paid_until = timezone.now() + timedelta(days=tariff['days'])
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()

        Payment.objects.create(
            order=self,
            customer=self.customer,
            amount=tariff['price'],
            tariff=tariff_key,
            tariff_name=tariff['name'],
            paid_until=self.placement_paid_until
        )

        return self.placement_paid_until

    def get_extra_services_list(self):
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
        base_price_per_sqm = BASE_PRICES_PER_SQM.get(self.cleaning_type, 0)
        base_price = base_price_per_sqm * self.area_sqm

        return {
            'cleaning_type': self.get_cleaning_type_display(),
            'area_sqm': float(self.area_sqm),
            'price_per_sqm': base_price_per_sqm,
            'base_price': float(base_price),
            'extra_services': self.get_extra_services_list(),
            'extra_total': float(self.extra_services_total),
            'urgency_fee': float(self.urgency_fee),
            'placement_price': float(self.placement_price),
            'total': float(self.total_price)
        }


class Payment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Заказ'
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Заказчик'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма (руб.)'
    )

    tariff = models.CharField(
        max_length=20,
        verbose_name='Тариф'
    )

    tariff_name = models.CharField(
        max_length=50,
        verbose_name='Название тарифа'
    )

    paid_until = models.DateTimeField(
        verbose_name='Оплата до'
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='paid',
        verbose_name='Статус'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата платежа')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']

    def __str__(self):
        return f"Платеж #{self.id} - {self.tariff_name} ({self.amount} руб.)"