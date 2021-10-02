from rest_framework import serializers


class GenericRequestSerializer(serializers.Serializer):
    request = serializers.CharField(required=True)