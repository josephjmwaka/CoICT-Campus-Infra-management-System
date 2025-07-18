from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from accounts.models import UserProfile
from infrastructure.models import (
    Block, Floor, Room, EquipmentCategory, 
    Equipment, Generator, MaintenanceRequest, MaintenanceLog
)
from .serializers import (
    UserSerializer, UserProfileSerializer,
    BlockSerializer, FloorSerializer, RoomSerializer,
    EquipmentCategorySerializer, EquipmentSerializer,
    GeneratorSerializer, MaintenanceRequestSerializer,
    MaintenanceLogSerializer, 
    MaintenanceSummarySerializer
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own profile unless they're staff
        user = self.request.user
        if user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BlockViewSet(viewsets.ModelViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        block_id = self.request.query_params.get('block_id')
        floor_id = self.request.query_params.get('floor_id')
        
        if block_id:
            queryset = queryset.filter(block_id=block_id)
        if floor_id:
            queryset = queryset.filter(floor_id=floor_id)
            
        return queryset

class EquipmentCategoryViewSet(viewsets.ModelViewSet):
    queryset = EquipmentCategory.objects.all()
    serializer_class = EquipmentCategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        room_id = self.request.query_params.get('room_id')
        category_id = self.request.query_params.get('category_id')
        
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset

class GeneratorViewSet(viewsets.ModelViewSet):
    queryset = Generator.objects.all()
    serializer_class = GeneratorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_staff:
            queryset = queryset.filter(reported_by=user)
            
        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        block_id = self.request.query_params.get('block_id')
        
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if block_id:
            queryset = queryset.filter(block_id=block_id)
            
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        request_obj = self.get_object()
        assigned_to_id = request.data.get('assigned_to_id')
        
        if not assigned_to_id:
            return Response(
                {'error': 'assigned_to_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            assigned_to = User.objects.get(pk=assigned_to_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        request_obj.assigned_to = assigned_to
        request_obj.status = 'ASSIGNED'
        request_obj.save()
        
        return Response(
            MaintenanceRequestSerializer(request_obj).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        request_obj = self.get_object()
        request_obj.status = 'COMPLETED'
        request_obj.completed_at = timezone.now()
        request_obj.save()
        
        return Response(
            MaintenanceRequestSerializer(request_obj).data,
            status=status.HTTP_200_OK
        )

class MaintenanceLogViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceLog.objects.all()
    serializer_class = MaintenanceLogSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(technician=self.request.user)
        


class MaintenanceSummaryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Get the requests reported by the authenticated user
        user_requests = MaintenanceRequest.objects.filter(reported_by=request.user)
        completed_requests = user_requests.filter(status='COMPLETED')
        in_progress_requests = user_requests.filter(status='IN_PROGRESS')

        # Prepare the summary data
        summary_data = {
            'total_requests': user_requests.count(),
            'completed_requests': completed_requests.count(),
            'in_progress_requests': in_progress_requests.count(),
        }

        # Serialize the summary data using the MaintenanceSummarySerializer
        serializer = MaintenanceSummarySerializer(summary_data)

        return Response(serializer.data)