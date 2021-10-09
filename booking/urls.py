from rest_framework.routers import DefaultRouter

from booking import views as book_views

router = DefaultRouter(trailing_slash=False)
router.register('booking', book_views.BoookingViewSet, 'booking')

urlpatterns = router.urls