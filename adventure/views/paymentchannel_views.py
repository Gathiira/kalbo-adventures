import logging

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from adventure import models as adv_models
from adventure import serializers as adv_serializers

log = logging.getLogger(__name__)


class PaymentChannelViewset(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = adv_models.PaymentChannel.objects.all().order_by('-date_created')

    def get_serializer_class(self):
        mapper = {
            "list": adv_serializers.ListPaymentChannelSerializer,
            "create": adv_serializers.CreatePaymentChannelSerializer,
            "update": adv_serializers.CreatePaymentChannelSerializer,
        }
        return mapper.get(self.action, None)

    def create(self, request, *args, **kwargs):
        payload = request.data
        serializer = adv_serializers.CreatePaymentChannelSerializer(data=payload, many=False)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            adventure = adv_models.PaymentChannel.objects.filter(account=payload['account'])
            if bool(adventure):
                adventure.name = payload['name']
                adventure.save()
        except Exception as e:
            log.error(e)
            print(payload)
            adventure = adv_models.PaymentChannel.objects.create(**payload)

        record_data = self.get_serializer_class()(adventure).data
        record_data.update({
            'id': str(adventure.id)
        })
        return Response(record_data)

    def update(self, request, *args, **kwargs):
        payload = request.data
        instance = self.get_object()
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        for field_name, field_value in payload.items():
            if hasattr(instance, field_name):
                setattr(instance, field_name, field_value)
        instance.save()

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"details": "Successfully deleted"}, status=status.HTTP_200_OK)