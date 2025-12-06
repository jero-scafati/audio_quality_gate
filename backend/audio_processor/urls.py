from rest_framework.routers import DefaultRouter
from .views import AudioAnalysisViewSet

router = DefaultRouter()
router.register(r'analyze', AudioAnalysisViewSet, basename='analyze')

urlpatterns = router.urls