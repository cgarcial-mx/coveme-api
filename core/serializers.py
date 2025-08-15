from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()  # Cambiar de username a email
    password = serializers.CharField(write_only=True)
    remember = serializers.BooleanField(required=False, default=False)  # Agregar campo remember
    
    def validate(self, attrs):
        print("🔍 Validating attrs:", attrs)
        
        email = attrs.get('email')
        password = attrs.get('password')
        
        print(f"🔍 Email: {email}, Password: {password}")
        
        if email and password:
            print("🔍 Both email and password provided")
            
            # Buscar usuario por email
            try:
                user = User.objects.get(email=email)
                print(f"🔍 User found: {user.username}")
                
                # Autenticar con username
                authenticated_user = authenticate(username=user.username, password=password)
                print(f"🔍 Authentication result: {authenticated_user}")
                
                if not authenticated_user:
                    raise serializers.ValidationError('Invalid credentials')
                if not authenticated_user.is_active:
                    raise serializers.ValidationError('User account is disabled')
                
                attrs['user'] = authenticated_user
                print("✅ Validation successful")
                return attrs
                
            except User.DoesNotExist:
                print("❌ User not found")
                raise serializers.ValidationError('User not found')
        else:
            print("❌ Missing email or password")
            raise serializers.ValidationError('Must include email and password')

class UserSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'client', 'client_name']
        read_only_fields = ['id']
    
    def get_client_name(self, obj):
        return obj.client.name if obj.client else None

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
