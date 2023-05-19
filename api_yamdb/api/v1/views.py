from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .mixins import CustomMixin
from .permissions import AdminOrReadOnly, ModerOrAuthorOrReadOnly
from .serializers import (CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          GETTitleSerializer,
                          ReviewSerializer,
                          TitleSerializer)


class CategoryViewSet(CustomMixin):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(CustomMixin):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_serializer_class(self):
        """Определение сериалайзера."""

        if self.request.method == 'GET':
            return GETTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ModerOrAuthorOrReadOnly,)

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
    permission_classes = (ModerOrAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
