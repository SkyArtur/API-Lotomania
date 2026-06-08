from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()

router.register('contests', views.ContestViewSet, basename='contests')
router.register('bets', views.BetViewSet, basename='bets')
router.register('numbers', views.NumberViewSet, basename='numbers')

urlpatterns = router.urls
