from rest_framework.routers import DefaultRouter

from blog import views

router = DefaultRouter(trailing_slash=False)
router.register('blog', views.BlogViewSet, 'blog')

print(router.urls)

urlpatterns = router.urls