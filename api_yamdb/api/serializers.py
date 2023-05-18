from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from reviews.models import Category, Comment, Genre, Review, Title, User


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True)
    confirmation_code = serializers.CharField(
        required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.SlugField(max_length=150)
    email = serializers.EmailField(max_length=254)

    def validate_username(self, username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                {"message": "недопустимый username"})
        return username

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            user = User.objects.get(username=data['username'])
            if user.email == data['email']:
                return data
            raise serializers.ValidationError({"message": "Неверный email"})
        return data

    class Meta:
        model = User
        fields = ('email', 'username')


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class GETTitleSerializer(serializers.ModelSerializer):
    """Сериалайзер для GET запроса."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    """Сериалайзер для произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        """Определение сериалайзера."""
        return GETTitleSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST':
            title_id = self.context['view'].kwargs['title_id']
            author = self.context['request'].user
            title = get_object_or_404(Title, pk=title_id)
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Можно оставить только один отзыв.'
                )
        return data

    def validate_score(self, value):
        if 0 > value > 10:
            raise serializers.ValidationError('Оценка по шкале от 1 до 10!')
        return value

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
