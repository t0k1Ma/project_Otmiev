from django.contrib.auth.models import AbstractUser
from django.db import models
from .constants import (
    ROLE_CHOICES,
    DEFAULT_CITY,
    AVATAR_UPLOAD_PATH,
)

class User(AbstractUser):

    
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    city = models.CharField(max_length=100, verbose_name='Город', default=DEFAULT_CITY)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer', verbose_name='Роль')
    avatar = models.ImageField(upload_to=AVATAR_UPLOAD_PATH, verbose_name='Аватар', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"



class ExecutorProfile(models.Model):
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='executor_profile',
        verbose_name='Пользователь'
    )

    specializations = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Специализация',
        help_text='Список типов уборок, которые выполняет'
    )

    experience_years = models.IntegerField(
        default=0,
        verbose_name='Опыт работы (лет)'
    )

    about = models.TextField(
        blank=True,
        verbose_name='О себе',
        help_text='Расскажите о своих преимуществах'
    )

    # Город и адрес исполнителя
    city = models.CharField(
        max_length=100,
        default='Москва',
        verbose_name='Город'
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Адрес (улица, дом)',
        help_text='Например: ул. Ленина, д. 10'
    )

    # Координаты (заполняются автоматически)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='Широта'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='Долгота'
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        verbose_name='Рейтинг'
    )

    total_orders = models.IntegerField(
        default=0,
        verbose_name='Выполнено заказов'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания профиля'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )


    class Meta:
        verbose_name = 'Профиль исполнителя'
        verbose_name_plural = 'Профили исполнителей'

    def __str__(self):
        return f"Профиль {self.user.username} ({self.city}, рейтинг: {self.rating})"
    
    def save(self, *args, **kwargs):
        update_coordinates = False
        
        if self.pk:
            try:
                old_profile = ExecutorProfile.objects.get(pk=self.pk)
                if old_profile.city != self.city or old_profile.address != self.address:
                    update_coordinates = True
            except ExecutorProfile.DoesNotExist:
                update_coordinates = True
        else:
            update_coordinates = True
        
        if update_coordinates and self.city:
            try:
                from geopy.geocoders import Nominatim
                geolocator = Nominatim(user_agent="otmiev_cleaning_app", timeout=10)
                full_address = f"{self.city}, {self.address}" if self.address else self.city
                location = geolocator.geocode(full_address)
                if location:
                    self.latitude = location.latitude
                    self.longitude = location.longitude
            except Exception as e:
                print(f"Не удалось получить координаты: {e}")
        
        super().save(*args, **kwargs)