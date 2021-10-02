from rest_framework import viewsets, permissions
from rest_framework.response import Response

from filemanager import models as file_models
from sharedservice import utility_functions

utility_function = utility_functions


class FileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)

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

    # def retrieve(self, request, *args, **kwargs):
    #     return Response()