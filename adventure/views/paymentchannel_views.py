from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from adventure import models as adv_models
from adventure import serializers as adv_serializers


class PaymentChannelViewset(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = adv_models.PaymentChannel.objects.all().order_by('-date_created')
    serializer_class = adv_serializers.ListPaymentChannelSerializer

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
            print(e)
            adventure = adv_models.PaymentChannel.objects.create(**payload)

        record_data = self.get_serializer_class()(adventure).data
        record_data.update({
            'id': str(adventure.id)
        })
        return Response(record_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"details": "Successfully deleted"}, status=status.HTTP_200_OK)