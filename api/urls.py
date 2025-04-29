from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserViewSet, UserProfileViewSet,
    BlockViewSet, FloorViewSet, RoomViewSet,
    EquipmentCategoryViewSet, EquipmentViewSet,
    GeneratorViewSet, MaintenanceRequestViewSet,
    MaintenanceLogViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'blocks', BlockViewSet)
router.register(r'floors', FloorViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'equipment-categories', EquipmentCategoryViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'generators', GeneratorViewSet)
router.register(r'maintenance-requests', MaintenanceRequestViewSet)
router.register(r'maintenance-logs', MaintenanceLogViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Infrastructure Management API",
        default_version='v1',
        description="API for managing campus infrastructure",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]