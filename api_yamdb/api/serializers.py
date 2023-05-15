from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


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

    class Meta:
        model = User
        fields = ('email', 'username')


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для категорий."""

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер для жанров."""

    class Meta:
        model = Genre
        exclude = ('id',)


class GETTitleSerializer(serializers.ModelSerializer):
    """Сериалайзер для GET запроса."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('__all__')


class TitleSerializer(serializers.ModelSerializer):
    """Сериалайзер для произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        exclude = ('id',)

    def to_representation(self, title):
        """Определение сериалайзера."""

        serializer = GETTitleSerializer
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate_rating(self, value):
        if 0 > value > 10:
            raise serializers.ValidationError('Оценка по шкале от 1 до 10!')
        return value

    class Meta:
        fields = '__all__'
        model = Review
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('title', 'author',),
                message='Один отзыв на одно произведение!'
            )
        ]


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
