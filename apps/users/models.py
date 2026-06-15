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



class ExecutorProfile(models.Model):

    #Профиль исполнителя

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='executor_profile',
        verbose_name='Пользователь'
    )
    
    SPECIALIZATION_CHOICES = (
        ('standard', 'Стандартная уборка'),
        ('xim_cleaning', 'Химчистка коворов/диванов'),
        ('after_repair', 'После ремонта'),
        ('office', 'Офисная уборка'),
    )
    
    specializations = models.JSONField(default=list,blank=True,verbose_name='Специализация',help_text='Список типов уборок, которые выполняет')
    experience_years = models.IntegerField(default="Менее года",verbose_name='Опыт работы')
    about = models.TextField(blank=True,verbose_name='О себе',help_text='Расскажите о своих преимуществах')
    latitude = models.DecimalField(max_digits=9,decimal_places=6,blank=True,null=True,verbose_name='Широта')
    longitude = models.DecimalField(max_digits=9,decimal_places=6,blank=True,null=True,verbose_name='Долгота')
    rating = models.DecimalField(max_digits=3,decimal_places=2,default=0,verbose_name='Рейтинг')
    total_orders = models.IntegerField(default=0,verbose_name='Выполнено заказов') 
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='Дата создания профиля')
    updated_at = models.DateTimeField(auto_now=True,verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Профиль исполнителя'
        verbose_name_plural = 'Профили исполнителей'
    
    def __str__(self):
        return f"Профиль {self.user.username} (рейтинг: {self.rating})"