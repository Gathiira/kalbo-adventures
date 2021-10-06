from rest_framework.routers import DefaultRouter

from adventure.views import adventure_views, paymentchannel_views, category_views

router = DefaultRouter(trailing_slash=False)
router.register('adventure', adventure_views.AdventureViewset, 'adventure')
router.register('payment-channel', paymentchannel_views.PaymentChannelViewset, 'payment-channel')
router.register('category', category_views.CategoryViewset, 'category')

urlpatterns = router.urls