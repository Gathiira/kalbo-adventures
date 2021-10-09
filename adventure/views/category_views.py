import logging

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from adventure import models as adv_models
from adventure import serializers as adv_serializers

log = logging.getLogger(__name__)


class CategoryViewset(viewsets.ModelViewSet):
    queryset = adv_models.Category.objects.all().order_by('name')
    serializer_class = adv_serializers.ListCategorySerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ['create', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, ]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        payload = request.data
        serializer = adv_serializers.CreateCategorySerializer(data=payload, many=False)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            category = adv_models.Category.objects.filter(account=payload['name'])
            if bool(category):
                category.name = payload['name']
                category.save()
        except Exception as e:
            log.error(e)
            category = adv_models.Category.objects.create(**payload)

        record_data = self.get_serializer_class()(category).data
        record_data.update({
            'id': str(category.id)
        })
        return Response(record_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"details": "Successfully deleted"}, status=status.HTTP_200_OK)