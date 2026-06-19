from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User, ExecutorProfile
from .serializers import UserSerializer, RegisterSerializer, ExecutorProfileSerializer
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser


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
    """Получение и обновление профиля исполнителя"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Проверяем что пользователь - исполнитель
        if request.user.role != 'executor':
            return Response({'error': 'Доступ запрещен'}, status=403)
        
        # Получаем или создаём профиль
        profile, created = ExecutorProfile.objects.get_or_create(user=request.user)
        
        serializer = ExecutorProfileSerializer(profile)
        return Response(serializer.data)
    
    def put(self, request):
        if request.user.role != 'executor':
            return Response({'error': 'Доступ запрещен'}, status=403)
        
        profile, created = ExecutorProfile.objects.get_or_create(user=request.user)
        
        # Обновляем данные пользователя (включая avatar если есть)
        if 'first_name' in request.data:
            request.user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            request.user.last_name = request.data['last_name']
        if 'city' in request.data:
            request.user.city = request.data['city']
        if 'email' in request.data:
            request.user.email = request.data['email']
        # avatar НЕ передаём через этот endpoint - только через upload-avatar/
        request.user.save()
        
        # Подготавливаем данные для профиля (исключаем поля пользователя)
        profile_data = {}
        for field in ['specializations', 'experience_years', 'about', 'address']:
            if field in request.data:
                profile_data[field] = request.data[field]
        
        # Обновляем профиль
        serializer = ExecutorProfileSerializer(profile, data=profile_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=400)
    
class UploadAvatarView(APIView):
    """Загрузка аватара пользователя"""
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        user = request.user
        
        # Получаем файл из запросса
        if 'avatar' not in request.FILES:
            return Response({'error': 'Файл не найден'}, status=400)
        
        # Удаляем старый аватар если есть
        if user.avatar:
            user.avatar.delete()
        
        # Сохраняем новый аватар
        user.avatar = request.FILES['avatar']
        user.save()
        
        # Возвращаем URL аватара
        return Response({
            'avatar_url': request.build_absolute_uri(user.avatar.url),
            'message': 'Аватар загружен'
        })