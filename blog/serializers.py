import logging

from rest_framework import serializers

from blog import models as blog_models
from filemanager import models as file_models
from filemanager.serializers import CATEGORIES

log = logging.getLogger(__name__)


class GenericRequestSerializer(serializers.Serializer):
    request = serializers.CharField(required=True)


class CreateImageSerializer(serializers.Serializer):
    image = serializers.CharField(required=True)
    category = serializers.ChoiceField(required=True, choices=CATEGORIES)


class CreateBlogSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    images = serializers.ListField(allow_empty=True, child=CreateImageSerializer())

    def validate(self, attrs):
        images = [image['image'] for image in attrs['images']]
        images_instances = file_models.Poster.objects.filter(id__in=images)
        if len(images) != images_instances.count():
            raise serializers.ValidationError('Invalid images provided')

        return attrs


class ListBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = blog_models.Blog
        fields = [
            'slug', 'title',
            'content', 'status',
            'date_created',
            'updated_on',
            'author',
        ]


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_image')

    class Meta:
        model = blog_models.Image
        fields = ['image', 'url', 'category']

    def get_image(self, obj):
        try:
            request = self.context.get('request')
            image_id = obj.image
            image = file_models.Poster.objects.get(id=image_id)
            url = request.build_absolute_uri(image.poster.url)
            return url
        except Exception as e:
            log.error(e)
            return []


class BlogDetailSerializer(ListBlogSerializer):
    images = ImageSerializer(many=True)

    class Meta:
        model = blog_models.Blog
        fields = ListBlogSerializer.Meta.fields + [
            'images'
        ]