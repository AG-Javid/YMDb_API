import uuid

from django.core.mail import EmailMessage
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from reviews.models import Category, Genre, Review, Title, User

from api_yamdb.settings import EMAIL_HOST_USER
from .permissions import AdminOnly, StaffOrAuthorOrReadOnly
from .serializers import (GetTokenSerializer, ReviewSerializer,
                          SignUpSerializer, UsersSerializer,
                          TitleSerializer, CategorySerializer,
                          GETTitleSerializer, GenreSerializer,
                          CommentSerializer)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AdminOnly, permissions.IsAuthenticated,)
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ('=username',)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me')
    def get_self_info(self, request):
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'GET':
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer.validate_data['role'] = request.user.role
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIGetTokenView(APIView):
    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return Response(
                {'username': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND)
        if data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        return Response(
            {'confirmation_code': 'Некорректный код подтверждения.'},
            status=status.HTTP_400_BAD_REQUEST)


def generate_confirm_code():
    return uuid.uuid4()


class APISignUpView(APIView):
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=(data['to_email'],),
            from_email=EMAIL_HOST_USER
        )
        email.send()

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        email = serializer.validated_data.get("email")
        user, created = User.objects.get_or_create(
            username=username, email=email)
        user.confirmation_code = generate_confirm_code()
        user.save()
        email_body = (
            f'Здравствуйте, {username}.'
            f'\nВаш код подтверждения для API: {user.confirmation_code}')
        data = {
            'email_body': email_body,
            'to_email': email,
            'email_subject': 'Код подтверждения для доступа к API.'
        }
        self.send_email(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (StaffOrAuthorOrReadOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (StaffOrAuthorOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.annotate(rating=Avg('reviews__rating'))
    serializer_class = TitleSerializer
    permission_classes = (StaffOrAuthorOrReadOnly, AdminOnly)

    def get_serializer_class(self):
        """Определение сериалайзера."""

        if self.request.method == 'GET':
            return GETTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (StaffOrAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (StaffOrAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('title_id'))

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
