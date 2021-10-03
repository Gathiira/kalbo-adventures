# Create your views here.
import logging

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from authentication.serializers import (
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer, ListUserSerializer
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
        except TokenError as e:
            log.error(e)
            raise InvalidToken(e.args[0])

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