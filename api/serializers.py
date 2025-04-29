from rest_framework import serializers
from accounts.models import UserProfile
from infrastructure.models import (
    Block, Floor, Room, EquipmentCategory, 
    Equipment, Generator, MaintenanceRequest, MaintenanceLog
)
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra responses here
        data['user'] = UserSerializer(self.user).data
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'

class FloorSerializer(serializers.ModelSerializer):
    block = BlockSerializer(read_only=True)
    block_id = serializers.PrimaryKeyRelatedField(
        queryset=Block.objects.filter(code__in=['A', 'B']),
        source='block',
        write_only=True
    )
    
    class Meta:
        model = Floor
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    block = BlockSerializer(read_only=True)
    block_id = serializers.PrimaryKeyRelatedField(
        queryset=Block.objects.all(),
        source='block',
        write_only=True
    )
    floor = FloorSerializer(read_only=True, allow_null=True)
    floor_id = serializers.PrimaryKeyRelatedField(
        queryset=Floor.objects.all(),
        source='floor',
        write_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Room
        fields = '__all__'
    
    def validate(self, data):
        block = data.get('block')
        floor = data.get('floor')
        
        if block and floor and floor.block != block:
            raise serializers.ValidationError("Floor must belong to the selected block")
        
        if block and not block.has_multiple_floors and floor:
            raise serializers.ValidationError("This block doesn't have floors")
            
        return data

class EquipmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentCategory
        fields = '__all__'

class EquipmentSerializer(serializers.ModelSerializer):
    category = EquipmentCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=EquipmentCategory.objects.all(),
        source='category',
        write_only=True
    )
    room = RoomSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        source='room',
        write_only=True
    )
    
    class Meta:
        model = Equipment
        fields = '__all__'

class GeneratorSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.filter(is_generator_room=True),
        source='room',
        write_only=True
    )
    
    class Meta:
        model = Generator
        fields = '__all__'

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    block = BlockSerializer(read_only=True)
    block_id = serializers.PrimaryKeyRelatedField(
        queryset=Block.objects.all(),
        source='block',
        write_only=True
    )
    floor = FloorSerializer(read_only=True, allow_null=True)
    floor_id = serializers.PrimaryKeyRelatedField(
        queryset=Floor.objects.all(),
        source='floor',
        write_only=True,
        allow_null=True
    )
    room = RoomSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        source='room',
        write_only=True
    )
    equipment = EquipmentSerializer(read_only=True, allow_null=True)
    equipment_id = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all(),
        source='equipment',
        write_only=True,
        allow_null=True
    )
    reported_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True, allow_null=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        allow_null=True
    )
    
    class Meta:
        model = MaintenanceRequest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'reported_by']

class MaintenanceLogSerializer(serializers.ModelSerializer):
    request = MaintenanceRequestSerializer(read_only=True)
    request_id = serializers.PrimaryKeyRelatedField(
        queryset=MaintenanceRequest.objects.all(),
        source='request',
        write_only=True
    )
    technician = UserSerializer(read_only=True)
    technician_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='technician',
        write_only=True
    )
    
    class Meta:
        model = MaintenanceLog
        fields = '__all__'
        read_only_fields = ['completion_date']