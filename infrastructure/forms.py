from django import forms
from .models import MaintenanceRequest, Equipment, Room, Block, Floor
class MaintenanceRequestForm(forms.ModelForm):
    equipment_name = forms.CharField(required=True, widget=forms.HiddenInput())  # Changed to required=True
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'block', 'floor', 'room', 'equipment_name',
            'model_number', 'serial_number', 'quantity',
            'issue_type', 'problem', 'description', 'priority', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['model_number'].required = False
        self.fields['serial_number'].required = False
        self.fields['quantity'].required = False

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        equipment_name = cleaned_data.get('equipment_name')
        model_number = cleaned_data.get('model_number')
        serial_number = cleaned_data.get('serial_number')
        quantity = cleaned_data.get('quantity', 1)

        if not room:
            self.add_error('room', 'Please select a room')
        
        if not equipment_name:
            self.add_error('equipment_name', 'Please select an equipment')
            return cleaned_data  # Return early if no equipment selected
        
        if model_number or serial_number:
            if not Equipment.objects.filter(
                room=room,
                name=equipment_name,
                model_number=model_number,
                serial_number=serial_number
            ).exists():
                self.add_error(None, 'No matching equipment found with these details')
        elif not quantity or quantity < 1:
            self.add_error('quantity', 'Please specify a valid quantity (at least 1)')

        return cleaned_data

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = '__all__'