from django.contrib import admin
from .models import User, ExecutorProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    #Настройка отображения пользователей в админке

    list_display = ('username', 'email', 'phone', 'city', 'role', 'created_at',)
    
    # По каким полям можно фильтровать
    list_filter = ('role', 'city', 'is_active')
    
    # По каким полям можно искать
    search_fields = ('username', 'email', 'phone')
    
    # Какие поля редактировать прямо в списке
    list_editable = ('role', 'city')

@admin.register(ExecutorProfile)
class ExecutorProfileAdmin(admin.ModelAdmin):

    #Настройка отображения профилей исполнителей
    
    list_display = ('user', 'rating', 'experience_years', 'total_orders')
    
    # По каким полям фильтровать
    list_filter = ('experience_years',)
    
    # По каким полям искать
    search_fields = ('user__username', 'user__email')
    
    # Какие поля редактировать прямо в списке
    list_editable = ('rating', 'experience_years')