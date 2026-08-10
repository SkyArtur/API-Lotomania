from rest_framework.routers import DefaultRouter
from . import views


app_name = 'api'

router = DefaultRouter()

router.register('sorteios', views.SorteioViewSet, basename='sorteios')
router.register('apostas', views.ApostaViewSet, basename='apostas')
router.register('numeros', views.NumeroViewSet, basename='numeros')
router.register('apostador', views.ApostadorViewSet, basename='apostador')

urlpatterns = router.urls
