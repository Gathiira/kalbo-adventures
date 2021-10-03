import logging

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from filemanager import models as file_models
from filemanager import serializers as file_serializers
from sharedservice import utility_functions

utility_function = utility_functions

log = logging.getLogger(__name__)


class FileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = file_serializers.FileDetailsSerializer
    queryset = file_models.Poster.objects.all().order_by('-date_created')

    def create(self, request, *args, **kwargs):
        payload = request.data.items()
        all_images = []
        for key, _ in payload:
            images = request.FILES.getlist(key)
            for image in images:
                if image.size > 15360 * 1024:
                    return Response(
                        {'details': 'File is too large'},
                        status=status.HTTP_400_BAD_REQUEST)

                allowed_extension = ['.jpeg', '.jpg', '.png', ]
                file_details = utility_function.split_text(image.name)
                extension = file_details[1]
                if extension not in allowed_extension:
                    return Response(
                        {"details": "Invalid image"},
                        status=status.HTTP_400_BAD_REQUEST)
                image_param = {
                    "name": file_details[0],
                    "poster": image,
                }
                image_inst = file_models.Poster.objects.create(**image_param)
                all_images.append(image_inst.id)

        return Response(all_images)

    @action(
        methods=['DELETE'],
        detail=False,
        url_name='clean-files',
        url_path='clean-files',
    )
    def clean_files(self, request, *args, **kwargs):
        instances = file_models.Poster.objects.filter(is_referenced=False)
        for instance in instances:
            self.perform_destroy(instance)
        return Response("success")

    @action(
        methods=['POST'],
        detail=False,
        url_name='categorize-file',
        url_path='categorize-file',
    )
    def categorize_file(self, request, *args, **kwargs):
        payload = request.data
        serializer = file_serializers.CategorizeFileSerializer(data=payload, many=False)
        serializer.is_valid(raise_exception=True)
        request = payload['request']
        try:
            queryset = file_models.Poster.objects.get(id=request)
        except Exception as e:
            log.error(e)
            return Response({"details": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        category = payload['category']
        queryset.category = category
        queryset.save(update_fields=['category'])
        return Response({"details": "Updated successfully"})