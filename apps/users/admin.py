from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    #Настройка отображения пользователей в админке

    # Какие колонки показывать в списке
    list_display = ('username', 'email', 'phone', 'city', 'role', 'created_at')
    
    # По каким полям можно фильтровать
    list_filter = ('role', 'city', 'is_active')
    
    # По каким полям можно искать
    search_fields = ('username', 'email', 'phone')
    
    # Какие поля редактировать прямо в списке
    list_editable = ('role', 'city')