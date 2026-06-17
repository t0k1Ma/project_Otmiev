from django.contrib import admin
from django import forms
from .models import User, ExecutorProfile


class ExecutorProfileAdminForm(forms.ModelForm):
    
    specializations = forms.MultipleChoiceField(
        choices=[
            ('standard', 'Стандартная уборка'),
            ('general', 'Генеральная уборка'),
            ('after_repair', 'После ремонта'),
            ('office', 'Офисная уборка'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Специализация'
    )
    
    class Meta:
        model = ExecutorProfile
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.cleaned_data.get('specializations'):
            instance.specializations = self.cleaned_data['specializations']
        else:
            instance.specializations = []
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


@admin.register(ExecutorProfile)
class ExecutorProfileAdmin(admin.ModelAdmin):
    form = ExecutorProfileAdminForm
    
    list_display = ('user', 'city', 'rating', 'total_orders', 'experience_years')
    list_filter = ('specializations', 'city', 'created_at')
    search_fields = ('user__username', 'user__email', 'city')
    
    readonly_fields = (
        'rating', 'total_orders', 'created_at', 'updated_at',
        'latitude', 'longitude'
    )
    
    fieldsets = (
        ('Основное', {
            'fields': ('user', 'city', 'address', 'specializations', 'experience_years', 'about')
        }),
        ('Координаты (автоматически)', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',),
            'description': 'Заполняются автоматически. Не редактируйте вручную!'
        }),
        ('Статистика', {
            'fields': ('rating', 'total_orders', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'city', 'is_active')
    list_filter = ('role', 'is_active', 'city')
    search_fields = ('username', 'email', 'first_name', 'last_name')