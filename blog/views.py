from django.db import IntegrityError
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from blog import models as blog_models
from blog import serializers as blog_serializers


class BlogViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'slug'

    def get_serializer_class(self):
        mapper = {
            "list": blog_serializers.ListBlogSerializer,
            "create": blog_serializers.CreateBlogSerializer,
            "retrieve": blog_serializers.BlogDetailSerializer,
        }
        return mapper.get(self.action, None)

    def get_permissions(self):
        permission_classes = []

        if self.action in ['create', 'update', 'destroy', 'publish']:
            permission_classes = [permissions.IsAuthenticated, ]

        return [permission() for permission in permission_classes]

    def get_authenticated_user(self):
        return self.request.user

    def is_authenticated_user(self):
        return self.request.user.is_authenticated

    def get_authenticated_user_id(self):
        return self.get_authenticated_user().id

    def get_queryset(self):
        owner = self.request.query_params.get('filter')
        if not owner and self.is_authenticated_user():
            return blog_models.Blog.objects.filter(
                Q(author__id=self.get_authenticated_user_id()) | Q(status='PUBLISH'))
        if self.is_authenticated_user():
            return blog_models.Blog.objects.filter(author__id=self.get_authenticated_user_id())
        return blog_models.Blog.objects.filter(status='PUBLISH')

    def create(self, request, *args, **kwargs):
        payload = request.data
        serializer = self.get_serializer(data=payload, many=False)
        serializer.is_valid(raise_exception=True)
        blog_payload = {
            "title": payload['title'],
            "content": payload['content'],
            "status": "DRAFT",
            "author": self.get_authenticated_user()
        }

        try:
            blog = blog_models.Blog.objects.create(**blog_payload)
        except IntegrityError:
            return Response({"details": "Failed to process request. Try again later"},
                            status=status.HTTP_400_BAD_REQUEST)

        for image in payload['images']:
            image_payload = {
                "blog": blog,
                "image": image['image'],
                "category": image['category'],
            }
            blog_models.Image.objects.create(**image_payload)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"details": "Blog deleted"}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, url_path='publish', url_name='publish')
    def publish(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'PUBLISH'
        instance.save(update_fields=['status'])
        return Response({"details": "Blog published"}, status=status.HTTP_200_OK)