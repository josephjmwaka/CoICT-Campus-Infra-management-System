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
            return cleaned_data
        
        # Get base queryset for all matching equipment
        equipments = Equipment.objects.filter(
            room=room,
            name=equipment_name
        )
        
        # Case 1: Serial number provided (must be unique)
        if serial_number:
            try:
                equipment = equipments.get(serial_number=serial_number)
                cleaned_data['equipment'] = equipment
                cleaned_data['quantity'] = 1  # Serial numbers are unique
            except Equipment.DoesNotExist:
                self.add_error('serial_number', 'No equipment found with this serial number')
        
        # Case 2: Model number provided (can have multiple)
        elif model_number:
            matching_equipment = equipments.filter(model_number=model_number)
            total_available = matching_equipment.count()
            
            if total_available == 0:
                self.add_error('model_number', 'No equipment found with this model number')
            elif not quantity or quantity < 1:
                self.add_error('quantity', 'Please specify a valid quantity (at least 1)')
            elif quantity > total_available:
                self.add_error('quantity', 
                            f'Only {total_available} available with this model number')
            else:
                cleaned_data['total_available'] = total_available
        
        # Case 3: Neither provided - validate against total equipment count
        else:
            total_available = equipments.count()
            if not quantity or quantity < 1:
                self.add_error('quantity', 'Please specify a valid quantity (at least 1)')
            elif quantity > total_available:
                self.add_error('quantity', 
                            f'Only {total_available} available of this equipment')
            else:
                cleaned_data['total_available'] = total_available

        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.equipment and 'equipment_name' in self.cleaned_data:
            instance.equipment_name = self.cleaned_data['equipment_name']
        if commit:
            instance.save()
        return instance

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = '__all__'