from rest_framework import serializers
from .models import User, ExecutorProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'city', 'role', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone', 'city', 'role', 'first_name', 'last_name']
    
    def validate(self, attrs):
        # Проверка совпадения паролей
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')  # Убираем подтверждение
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            city=validated_data.get('city', 'Москва'),
            role=validated_data.get('role', 'customer'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class ExecutorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ExecutorProfile
        fields = ['id', 'user', 'specializations', 'experience_years', 'about',
                  'latitude', 'longitude', 'rating', 'total_orders']