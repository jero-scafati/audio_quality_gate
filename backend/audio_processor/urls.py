from rest_framework.routers import DefaultRouter
from .views import AudioAnalysisViewSet, AuditLogViewSet

router = DefaultRouter()
router.register(r'analyze', AudioAnalysisViewSet, basename='analyze')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')

urlpatterns = router.urls