from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    #Модель пользователя

    ROLE_CHOICES = (
        ('customer', 'Заказчик'),
        ('executor', 'Исполнитель'),
    )
    
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    city = models.CharField(max_length=100, verbose_name='Город', default='Ростов-на-Дону')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer', verbose_name='Роль')
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватар', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
