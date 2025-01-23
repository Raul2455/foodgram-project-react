from api.serializers import RecipeSmallSerializer
from rest_framework import serializers
from users.models import Subscription, User


class UserShowSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о пользователе."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с моделью пользователя."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(
        min_length=4,
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        """Проверяет, что email уникален."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return value

    def validate_username(self, value):
        """Проверяет, что имя пользователя уникально и не является запрещенным."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким именем уже существует.')
        return value

    def create(self, validated_data):
        """Создает нового пользователя с хешированием пароля."""
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """Обновляет данные пользователя."""
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    banned_names = ('me', 'admin', 'ADMIN', 'administrator', 'moderator')

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        """Проверяет, что имя пользователя не является запрещенным."""
        if value.lower() in self.banned_names:
            raise serializers.ValidationError('Использование этого имени запрещено.')
        return value

    def validate_email(self, value):
        """Проверяет, что email уникален."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return value


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """Проверяет учетные данные и возвращает токен."""
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = User.objects.filter(username=username).first()
            if user and user.check_password(password):
                return data
            raise serializers.ValidationError('Неверные учетные данные.')
        raise serializers.ValidationError('Необходимо указать имя пользователя и пароль.')


class SubShowSerializer(UserShowSerializer):
    """Сериализатор для отображения подписок с рецептами."""

    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserShowSerializer.Meta):
        fields = UserShowSerializer.Meta.fields + ('recipes',)

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                author=obj.following
            ).exists()
        return False

    def get_recipes(self, obj):
        """Возвращает список рецептов автора."""
        request = self.context.get('request')
        recipes = obj.following.recipes.all()[:3]  # Ограничиваем количество рецептов
        return RecipeSmallSerializer(recipes, many=True, context={'request': request}).data