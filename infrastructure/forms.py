from django import forms
from .models import MaintenanceRequest, Equipment, Room, Block, Floor

class MaintenanceRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit room choices based on block selection
        if 'block' in self.data:
            try:
                block_id = int(self.data.get('block'))
                self.fields['room'].queryset = Room.objects.filter(block_id=block_id)
            except (ValueError, TypeError):
                pass
        
        # Limit floor choices to only blocks A and B
        self.fields['floor'].queryset = Floor.objects.filter(block__code__in=['A', 'B'])
        
        # Limit equipment choices to the selected room
        if 'room' in self.data:
            try:
                room_id = int(self.data.get('room'))
                self.fields['equipment'].queryset = Equipment.objects.filter(room_id=room_id)
            except (ValueError, TypeError):
                pass
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'block', 'floor', 'room', 'equipment',
            'issue_type', 'title', 'description', 'priority', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['description'].required = False

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = '__all__'