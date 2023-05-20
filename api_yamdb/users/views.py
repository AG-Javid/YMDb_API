from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .models import User
from .confirm import send_conf_code
from users.serializers import (GetTokenSerializer,
                               SignUpSerializer,
                               UsersSerializer)
from api.v1.permissions import AdminOnly


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AdminOnly,)
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ('=username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = UsersSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'GET':
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer.validated_data['role'] = request.user.role
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIGetTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User,
                                 username=data.get('username'))
        access_token = AccessToken.for_user(user)
        confirm_code = data['confirmation_code']
        if not default_token_generator.check_token(
            user,
            confirm_code
        ):
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'token': str(access_token)},
                        status=status.HTTP_200_OK)


class APISignUpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, created = User.objects.get_or_create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email']
            )
        except IntegrityError:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if user or created:
            send_conf_code(serializer.data.get('username'))
        return Response(serializer.data, status=status.HTTP_200_OK)
