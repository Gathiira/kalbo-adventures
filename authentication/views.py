# Create your views here.
import logging

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from authentication.serializers import (
    MyTokenObtainPairSerializer,
    RegisterSerializer, ResetPassSerializer,
    UserSerializer, ListUserSerializer, CreateUserSerializer
)

User = get_user_model()

log = logging.getLogger(__name__)


class MyObtainTokenPairView(viewsets.ModelViewSet):

    def get_serializer_class(self):
        mapper = {
            "login": MyTokenObtainPairSerializer,
            "register": RegisterSerializer,
            "user_details": UserSerializer,
            "list": ListUserSerializer,
            "user_register": CreateUserSerializer,
            "reset_password": ResetPassSerializer,
        }
        return mapper.get(self.action, MyTokenObtainPairSerializer)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'user_details':
            permission_classes = [permissions.IsAuthenticated, ]

        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated, ]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_registered')
        return queryset

    @action(methods=['POST'], detail=False, url_name='login', url_path='login')
    def login(self, request):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            log.error(e)
            return Response({"details": "No active account found with the given credentials"},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_name='register', url_path='register')
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(
        methods=['GET'],
        detail=False,
        url_name='user-profile',
        url_path='user-profile'
    )
    def user_details(self, request):
        authenticated_user = request.user
        try:
            user_details = get_user_model().objects.get(id=authenticated_user.id)
            records = self.get_serializer(user_details, many=False)
            status_code = status.HTTP_200_OK
            response = records.data
        except Exception as e:
            log.error(e)
            status_code = status.HTTP_400_BAD_REQUEST
            response = {"details": str(e)}

        return Response(response, status=status_code)

    @action(methods=['POST'], detail=False, url_name='reset-password', url_path='reset-password')
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = request.data
        try:
            user = User.objects.get(email=payload['email'])
        except Exception as e:
            log.error(e)
            return Response({"details": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(payload['password'])
        user.save(update_fields=['password'])
        return Response({"details": "Password Reset Successfully"}, status=status.HTTP_200_OK)