from rest_framework.routers import DefaultRouter

from authentication.views import MyObtainTokenPairView

app_name = 'authentication'

router = DefaultRouter(trailing_slash=False)
router.register('account', MyObtainTokenPairView, 'account')

urlpatterns = router.urls