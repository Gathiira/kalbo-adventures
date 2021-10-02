from rest_framework.routers import DefaultRouter

from authentication.views import MyObtainTokenPairView

#
# urlpatterns = [
#     # path('login', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
#     path('login/refresh', TokenRefreshView.as_view(), name='token_refresh'),
#     path('register', RegisterView.as_view(), name='auth_register'),
#     path('user-profile', UserProfileView.as_view(), name='auth_profile'),
# ]

router = DefaultRouter(trailing_slash=False)
router.register('account', MyObtainTokenPairView, 'account')

urlpatterns = router.urls