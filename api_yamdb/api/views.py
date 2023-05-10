import uuid

from django.core.mail import EmailMessage
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User
from .permissions import AdminOnly
from .serializers import (GetTokenSerializer, SignUpSerializer,
                          UsersSerializer)


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
            to=data['to_email']
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
