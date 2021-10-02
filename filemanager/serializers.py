from rest_framework import serializers

from filemanager import models as file_models


class GenericRequestSerializer(serializers.Serializer):
    request = serializers.CharField(required=True)


class FileDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = file_models.Poster
        fields = '__all__'


CATEGORIES = [
    "MAIN", "PIC1", "PIC2", 'PIC3', 'PIC4',
    'PIC5', 'PIC6', 'PIC7', 'PIC8', 'PIC9', 'PIC10'
]


class CategorizeFileSerializer(GenericRequestSerializer):
    category = serializers.ChoiceField(required=True, choices=CATEGORIES)