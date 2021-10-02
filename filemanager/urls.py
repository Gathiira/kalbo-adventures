from rest_framework.routers import DefaultRouter

from filemanager.views import FileViewSet

router = DefaultRouter(trailing_slash=False)
router.register('filemanager', FileViewSet, basename='filemanager'),

urlpatterns = router.urls