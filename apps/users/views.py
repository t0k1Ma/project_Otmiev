from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User, ExecutorProfile
from .serializers import UserSerializer, RegisterSerializer, ExecutorProfileSerializer
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Пользователь успешно зарегистрирован'  
        }, status=status.HTTP_201_CREATED)  #

class CheckUsernameView(generics.GenericAPIView):
    """Проверка уникальности username"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        username = request.query_params.get('username', '')
        exists = User.objects.filter(username=username).exists()
        return Response({'exists': exists})

class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            })
        return Response({'error': 'Неверные данные'}, status=400)


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.all()


class ExecutorProfileListView(generics.ListAPIView):
    serializer_class = ExecutorProfileSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return ExecutorProfile.objects.all()


def login_view(request):
    """Страница входа"""
    return render(request, 'login.html')


class ExecutorProfileView(APIView):
    """Получить профиль исполнителя"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Проверяем что пользователь - исполнитель
        if request.user.role != 'executor':
            return Response({'error': 'Доступ запрещен'}, status=403)
        
        # Получаем профиль
        try:
            profile = request.user.executor_profile
            serializer = ExecutorProfileSerializer(profile)
            return Response(serializer.data)
        except ExecutorProfile.DoesNotExist:
            return Response({'error': 'Профиль не найден'}, status=404)